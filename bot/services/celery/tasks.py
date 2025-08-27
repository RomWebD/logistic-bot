# bot/services/celery/tasks.py
import asyncio
from bot.celery_app import celery_app
from bot.services.celery.task_tracker import clear_sheet_job, set_sheet_job
from bot.services.google_services.sheets_client import RequestSheetManager
from bot.services.google_services.utils import request_to_row
from bot.services.celery.messenger import queue_bot_message

from bot.database.database import async_session
from bot.repositories.client_repository import ClientRepository
from bot.repositories.google_sheet_repository import GoogleSheetRepository
from bot.repositories.shipment_repository import ShipmentRepository
from bot.models.google_sheets_binding import OwnerType, SheetType, SheetStatus


def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@celery_app.task(name="ensure_client_request_sheet", bind=True)
def ensure_client_request_sheet(self, tg_id: int):
    set_sheet_job(tg_id, self.request.id)
    try:

        async def _work():
            async with async_session() as session:
                client_repo = ClientRepository(session)
                sheet_repo = GoogleSheetRepository(session)

                client = await client_repo.get_by_telegram_id(tg_id)
                if not client:
                    return

                # ставимо статус CREATING (якщо ще не READY)
                binding = await sheet_repo.get_or_create(
                    telegram_id=tg_id,
                    owner_type=OwnerType.CLIENT,
                    sheet_type=SheetType.REQUESTS,
                )
                if binding.status != SheetStatus.READY:
                    await sheet_repo.update_status(binding.id, SheetStatus.CREATING)

                manager = RequestSheetManager()
                sheet_id, sheet_url = manager.ensure_request_sheet_for_client(
                    tg_id=tg_id,
                    client_full_name=client.full_name,
                    client_email=client.email,
                    google_sheet_id=binding.sheet_id,
                    google_sheet_url=binding.sheet_url,
                )

                # оновлюємо/створюємо прив’язку та ставимо READY
                await sheet_repo.create_or_update(
                    telegram_id=tg_id,
                    owner_type=OwnerType.CLIENT,
                    sheet_type=SheetType.REQUESTS,
                    sheet_id=sheet_id,
                    sheet_url=sheet_url,
                )

                kb = {
                    "inline_keyboard": [
                        [{"text": "🔗 Мої заявки", "url": sheet_url}],
                        [
                            {
                                "text": "✍️ Створити нову заявку",
                                "callback_data": "client_application",
                            }
                        ],
                    ]
                }
                queue_bot_message(
                    tg_id, "✅ Ваш Google Sheet з заявками успішно створено!", kb
                )

        run_async(_work())
    finally:
        clear_sheet_job(tg_id)


@celery_app.task(name="append_request_to_sheet")
def append_request_to_sheet(tg_id: int, request_id: int):
    async def _work():
        async with async_session() as session:
            client_repo = ClientRepository(session)
            sheet_repo = GoogleSheetRepository(session)
            shipment_repo = ShipmentRepository(session)

            client = await client_repo.get_by_telegram_id(tg_id)
            req = await shipment_repo.get_request_by_id(request_id)
            if not client or not req:
                return

            mgr = RequestSheetManager()
            # гарантуємо таблицю (і заодно отримуємо id/url)
            sheet_id, sheet_url = mgr.ensure_request_sheet_for_client(
                tg_id=tg_id,
                client_full_name=client.full_name,
                client_email=client.email,
                google_sheet_id=None,
                google_sheet_url=None,
            )
            # оновлюємо/створюємо binding
            await sheet_repo.create_or_update(
                telegram_id=tg_id,
                owner_type=OwnerType.CLIENT,
                sheet_type=SheetType.REQUESTS,
                sheet_id=sheet_id,
                sheet_url=sheet_url,
            )
            # додати рядок
            mgr.svc_sheets.put_row(sheet_id, "Заявки", request_to_row(req))

            kb = {
                "inline_keyboard": [
                    [{"text": "🔗 Мої заявки", "url": sheet_url}],
                    [
                        {
                            "text": "➕ Створити нову заявку",
                            "callback_data": "client_application",
                        }
                    ],
                ]
            }
            queue_bot_message(tg_id, "✅ Заявку додано у ваш Google Sheet.", kb)

    run_async(_work())


@celery_app.task(name="notify_carriers")
def notify_carriers_task(request_id: int):
    async def _work():
        async with async_session() as session:
            shipment_repo = ShipmentRepository(session)
            req = await shipment_repo.get_request_by_id(request_id)
            if not req:
                return
            # TODO: заміни на реальну логіку вибору перевізників
            target_carriers = getattr(req, "target_carriers", []) or []
            for carrier_id in target_carriers:
                queue_bot_message(carrier_id, f"🆕 Нова заявка #{req.id}")

    run_async(_work())


@celery_app.task(name="sync_client_requests_from_sheet")
def sync_client_requests_from_sheet(tg_id: int):
    # TODO: імплементація під нову схему (ревізії). Залишаю заглушку.
    pass


@celery_app.task(name="check_client_sheet_revisions")
def check_client_sheet_revisions():
    """
    Перевірка останніх ревізій таблиць клієнтів (READY + REQUESTS).
    """

    async def _work():
        async with async_session() as session:
            sheet_repo = GoogleSheetRepository(session)
            mgr = RequestSheetManager()

            bindings = await sheet_repo.get_ready_client_request_bindings()
            changes = []
            for b in bindings:
                # приклад: отримати інфо про останню ревізію (реалізуй у своєму менеджері)
                attempt = mgr.get_latest_revision_info(b.sheet_id, None)
                # або mgr.fetch_revisions(b.sheet_id)
                # Тут ти далі вирішуєш що робити (оновити last_revision_id тощо)
                # changes.append({...})
            return changes

    return run_async(_work())

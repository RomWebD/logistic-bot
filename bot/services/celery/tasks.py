from bot.celery_app import celery_app
from bot.database.database import get_session
from bot.models.shipment_request import Shipment_request
from bot.services.google_services.sheets_client import RequestSheetManager
from bot.handlers.client import crud
from bot.services.google_services.utils import request_to_row
from bot.services.loader import bot


@celery_app.task
def ensure_client_request_sheet(tg_id: int):
    """
    Фонова таска: створює (або перевіряє існуючий) Google Sheet для заявок клієнта.
    Коли готово — оновлює БД та надсилає повідомлення користувачу.
    """
    manager = RequestSheetManager()

    # Беремо з БД поточний client (щоб підтягнути google_sheet_id/url)
    import asyncio

    async def _do():
        client = await crud.get_client_by_telegram_id(tg_id)

        sheet_id, sheet_url = manager.ensure_request_sheet_for_client(
            tg_id=tg_id,
            client_full_name=client.full_name,
            client_email=client.email,
            google_sheet_id=client.google_sheet_id,
            google_sheet_url=client.google_sheet_url,
        )

        if (client.google_sheet_id != sheet_id) or (
            client.google_sheet_url != sheet_url
        ):
            await crud.update_client_sheet_by_telegram(tg_id, sheet_id, sheet_url)

        # сповіщаємо користувача у Telegram
        kb = {
            "inline_keyboard": [
                [{"text": "🔗 Відкрити заявки", "url": sheet_url}],
                [
                    {
                        "text": "✍️ Створити нову заявку",
                        "callback_data": "client_application",
                    }
                ],
            ]
        }
        await bot.send_message(
            tg_id,
            "✅ Ваш Google Sheet з заявками успішно створено!",
            reply_markup=kb,
        )

    asyncio.run(_do())


@celery_app.task
def ensure_sheet_and_append_request_row(tg_id: int, request_id: int):
    """
    1) беремо клієнта і заявку з БД (через crud)
    2) забезпечуємо файл (через RequestSheetManager)
    3) якщо файл новий — оновлюємо БД (через crud.ensure_client_sheet_binding)
    4) додаємо рядок у лист "Заявки"
    5) (опц.) можна надіслати юзеру нотифікацію
    """
    import asyncio

    async def _run():
        client, req = await crud.get_client_and_request(tg_id, request_id)
        if not client or not req:
            return

        mgr = RequestSheetManager()
        sheet_id, sheet_url = mgr.ensure_request_sheet_for_client(
            tg_id=tg_id,
            client_full_name=client.full_name,
            client_email=client.email,
            google_sheet_id=client.google_sheet_id,
            google_sheet_url=client.google_sheet_url,
        )

        # оновлюємо бінд, якщо треба
        await crud.ensure_client_sheet_binding(tg_id, sheet_id, sheet_url)

        # додаємо рядок
        mgr.svc_sheets.put_row(sheet_id, "Заявки", request_to_row(req))

        # (опційно) повідомлення юзеру
        try:
            kb = {
                "inline_keyboard": [[{"text": "🔗 Відкрити заявки", "url": sheet_url}]]
            }
            await bot.send_message(
                chat_id=tg_id,
                text="✅ Заявку додано у ваш Google Sheet.",
                reply_markup=kb,
            )
        except Exception:
            pass

    asyncio.run(_run())


@celery_app.task
def append_request_to_sheet_task(tg_id: int, request_id: int):
    """
    Додає заявку в Google Sheet клієнта.
    """
    import asyncio
    from bot.database.database import get_session
    from sqlalchemy.future import select
    from bot.models.client import Client

    async def _do():
        async for session in get_session():
            result = await session.execute(
                select(Shipment_request).where(Shipment_request.id == request_id)
            )
            request: Shipment_request | None = result.scalar_one_or_none()

            result = await session.execute(
                select(Client).where(Client.telegram_id == tg_id)
            )
            client: Client | None = result.scalar_one_or_none()

            if not request or not client or not client.google_sheet_id:
                return

            mgr = RequestSheetManager()
            mgr.svc_sheets.put_row(
                client.google_sheet_id, "Заявки", request_to_row(request)
            )

    asyncio.run(_do())


@celery_app.task
def notify_carriers_task(request_id: int):
    """
    Сповіщає перевізників про нову заявку.
    """
    import asyncio
    from bot.database.database import get_session
    from sqlalchemy.future import select

    async def _do():
        async for session in get_session():
            result = await session.execute(
                select(Shipment_request).where(Shipment_request.id == request_id)
            )
            request: Shipment_request | None = result.scalar_one_or_none()

            if not request:
                return

            from bot.services.notifier import notify_carriers

            await notify_carriers(bot, request)

    asyncio.run(_do())

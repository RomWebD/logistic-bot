# bot/services/celery/tasks.py
from bot.celery_app import celery_app
from bot.services.celery.task_tracker import clear_sheet_job, set_sheet_job
from bot.services.google_services.sheets_client import RequestSheetManager
from bot.services.google_services.utils import request_to_row
from bot.handlers.client import sync_crud as crud
from bot.services.celery.messenger import queue_bot_message  # 👈 новий шар


@celery_app.task(name="ensure_client_request_sheet", bind=True)
def ensure_client_request_sheet(self, tg_id: int):
    set_sheet_job(tg_id, self.request.id)
    try:
        client = crud.get_client_by_telegram_id(tg_id)  # 👈 синхронний варіант
        if not client:
            return

        manager = RequestSheetManager()

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
            crud.update_client_sheet_by_telegram(tg_id, sheet_id, sheet_url)

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
            tg_id,
            "✅ Ваш Google Sheet з заявками успішно створено!",
            kb,
        )
    finally:
        clear_sheet_job(tg_id)


@celery_app.task(name="append_request_to_sheet")
def append_request_to_sheet(tg_id: int, request_id: int):
    client, req = crud.get_client_and_request(tg_id, request_id)
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

    crud.ensure_client_sheet_binding(tg_id, sheet_id, sheet_url)
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


@celery_app.task(name="notify_carriers")
def notify_carriers_task(request_id: int):
    req = crud.get_request_by_id(request_id)
    if req:
        # notifier теж кладе повідомлення в Redis, не чіпає bot напряму
        for carrier_id in req.target_carriers:
            queue_bot_message(carrier_id, f"🆕 Нова заявка {req.title}")

# bot/handlers/client/sync_crud.py
import asyncio
from . import crud


def run(coro):
    return asyncio.run(coro)


def get_client_by_telegram_id(tg_id: int):
    return run(crud.get_client_by_telegram_id(tg_id))


def update_client_sheet_by_telegram(tg_id: int, sheet_id: str, sheet_url: str):
    return run(crud.update_client_sheet_by_telegram(tg_id, sheet_id, sheet_url))


def get_client_and_request(tg_id: int, request_id: int):
    return run(crud.get_client_and_request(tg_id, request_id))


def ensure_client_sheet_binding(tg_id: int, sheet_id: str, sheet_url: str):
    return run(crud.ensure_client_sheet_binding(tg_id, sheet_id, sheet_url))


def get_request_by_id(request_id: int):
    return run(crud.get_request_by_id(request_id))

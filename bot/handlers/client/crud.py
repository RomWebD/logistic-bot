from sqlalchemy import select
from bot.database.database import async_session
from bot.models import Client
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from typing import Optional


async def get_client_by_telegram_id(telegram_id: int) -> Optional[Client]:
    """
    Повертає екземпляр Client за telegram_id або None, якщо не знайдено.
    """
    async with async_session() as session:
        result = await session.execute(
            select(Client).where(Client.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


async def update_client_sheet_by_telegram(
    telegram_id: int, sheet_id: str, sheet_url: str
) -> None:
    async with async_session() as session:
        result = await session.execute(
            select(Client).where(Client.telegram_id == telegram_id)
        )
        client = result.scalar_one_or_none()

        if client:
            client.google_sheet_id = sheet_id
            client.google_sheet_url = sheet_url
            await session.commit()


# utils.py або crud.py
def build_vehicle_sheet_markup(sheet_url: str) -> InlineKeyboardMarkup:
    if sheet_url:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Мої заявки", url=sheet_url)],
                [
                    InlineKeyboardButton(
                        text="➕ Створити нову заявку",
                        callback_data="carrier_add_new_car",
                    )
                ],
            ]
        )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            InlineKeyboardButton(
                text="➕ Створити нову заявку",
                callback_data="client_create_new_request",
            )
        ],
    )

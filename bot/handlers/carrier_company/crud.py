from sqlalchemy import select
from bot.database.database import async_session
from bot.models import CarrierCompany
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


async def get_sheet_url_by_telegram_id(telegram_id: int) -> str | None:
    async with async_session() as session:
        result = await session.execute(
            select(CarrierCompany.google_sheet_url).where(
                CarrierCompany.telegram_id == telegram_id
            )
        )
        sheet_url = result.scalar()
        return sheet_url


# utils.py або crud.py
def build_vehicle_sheet_markup(sheet_url: str) -> InlineKeyboardMarkup:
    if sheet_url:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Відкрити автопарк", url=sheet_url)],
                [
                    InlineKeyboardButton(
                        text="➕ Добавити транспорт",
                        callback_data="carrier_add_new_car",
                    )
                ],
            ]
        )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            InlineKeyboardButton(
                text="➕ Добавити транспорт",
                callback_data="carrier_add_new_car",
            )
        ],
    )

# bot/services/notifier.py

from aiogram import Bot
from sqlalchemy import select
from bot.models import CarrierCompany
from bot.models.shipment_request import Shipment_request
from bot.database.database import async_session
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def notify_carriers(bot: Bot, request: Shipment_request):
    async with async_session() as session:
        carriers = await session.scalars(
            select(CarrierCompany).where(CarrierCompany.from_city == request.from_city)
        )

        for carrier in carriers:
            await bot.send_message(
                carrier.telegram_id,
                f"""📦 <b>Нова заявка на перевезення:</b>
Маршрут: {request.from_city} → {request.to_city}
Дата подачі: {request.date_text}
Тип вантажу: {request.cargo_type}
Обʼєм: {request.volume}
Орієнтовна вага: {request.weight}
Завантаження: {request.loading}
Вивантаження: {request.unloading}
Ціна: {request.price:,} грн""",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="✅ Прийняти рейс",
                                callback_data=f"accept_{request.id}",
                            ),
                            InlineKeyboardButton(
                                text="❌ Відмовитись",
                                callback_data=f"decline_{request.id}",
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                text="💬 Запропонувати іншу ставку",
                                callback_data=f"negotiate_{request.id}",
                            )
                        ],
                    ]
                ),
                parse_mode="HTML",
            )

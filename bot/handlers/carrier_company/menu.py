from aiogram import Router, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.filters import Command
from bot.decorators.access import require_verified_carrier

router = Router()

carrier_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🚚 Мої транспортні засоби", callback_data="carrier_vehicles"
            )
        ],
        [InlineKeyboardButton(text="📋 Мої заявки", callback_data="carrier_orders")],
        [
            InlineKeyboardButton(
                text="🔎 Пошук рейсів", callback_data="carrier_search_routes"
            )
        ],
        [
            InlineKeyboardButton(
                text="⚙️ Налаштування профілю", callback_data="carrier_settings"
            )
        ],
        [InlineKeyboardButton(text="🆘 Підтримка", callback_data="carrier_support")],
        [
            InlineKeyboardButton(
                text="💳 Фінанси (скоро)", callback_data="carrier_finance_disabled"
            )
        ],
    ]
)


# @router.callback_query(F.data == "open_carrier_menu")
@router.message(Command("menu"))
@require_verified_carrier()
async def handle_menu_command(message: Message):
    await message.answer("📂 Меню перевізника:", reply_markup=carrier_menu_keyboard)

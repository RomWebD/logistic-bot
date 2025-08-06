from aiogram import Router, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    WebAppInfo,
)
from aiogram.filters import Command
from bot.decorators.access import require_verified_carrier
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

# carrier_menu_keyboard = InlineKeyboardMarkup(
#     inline_keyboard=[
#         [
#             InlineKeyboardButton(
#                 text="🚚 Мої транспортні засоби", callback_data="carrier_vehicles"
#             )
#         ],
#         [InlineKeyboardButton(text="📋 Мої заявки", callback_data="carrier_orders")],
#         [
#             InlineKeyboardButton(
#                 text="🔎 Пошук рейсів", callback_data="carrier_search_routes"
#             )
#         ],
#         [
#             InlineKeyboardButton(
#                 text="⚙️ Налаштування профілю", callback_data="carrier_settings"
#             )
#         ],
#         [InlineKeyboardButton(text="🆘 Підтримка", callback_data="carrier_support")],
#         [
#             InlineKeyboardButton(
#                 text="💳 Фінанси (скоро)", callback_data="carrier_finance_disabled"
#             )
#         ],
#     ]
# )

# Вебапп-кнопка
vehicle_webapp_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Відкрити автопарк",
                web_app=WebAppInfo(
                    url="https://docs.google.com/spreadsheets/d/1-JthBRgXotzuJIZUxY-8jwDfwhtDUcicnfm5OtZYAXk/edit?usp=sharing"
                ),  # або твій WebApp
            )
        ],
        [
            InlineKeyboardButton(
                text="➕ Добавити транспорт",
                callback_data="carrier_add_new_car",  # або твій WebApp
            ),
        ],
    ]
)


# Обробка натискання текстової кнопки з ReplyKeyboardMarkup
@router.message(F.text == "🚚 Мої транспортні засоби")
async def handle_vehicles_button(message: Message):
    await message.answer(
        "🔗 Натисніть кнопку нижче, щоб переглянути ваш автопарк:",
        reply_markup=vehicle_webapp_markup,
    )


carrier_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🚚 Мої транспортні засоби"),
            KeyboardButton(text="📋 Мої заявки"),
        ],
        [KeyboardButton(text="🔎 Пошук рейсів")],
        [KeyboardButton(text="⚙️ Налаштування профілю")],
        [KeyboardButton(text="🆘 Підтримка")],
        [KeyboardButton(text="💳 Фінанси (скоро)")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Оберіть опцію",
    one_time_keyboard=False,  # ❗️це важливо — меню не зникає після натискання
)


# carrier_menu_keyboard = InlineKeyboardMarkup(
#     inline_keyboard=[
#         [InlineKeyboardButton(text="🚚 Мої транспортні засоби", callback_data="carrier_vehicles"),
#         InlineKeyboardButton(text="📋 Мої заявки", callback_data="carrier_orders"),
#         InlineKeyboardButton(text="🔎 Пошук рейсів", callback_data="carrier_search_routes")],
#         [InlineKeyboardButton(text="⚙️ Налаштування профілю", callback_data="carrier_settings")],
#         [InlineKeyboardButton(text="🆘 Підтримка", callback_data="carrier_support")],
#         [InlineKeyboardButton(text="💳 Фінанси (скоро)", callback_data="carrier_finance_disabled")],
#     ]
# )
async def show_carrier_menu(message: Message):
    await message.answer("📂 Меню перевізника:", reply_markup=carrier_menu_keyboard)


@router.message(Command("menu"))
@require_verified_carrier()
async def handle_menu_command(message: Message):
    await show_carrier_menu(message)


@router.callback_query(F.data == "menu")
@require_verified_carrier()
async def handle_menu_callback(callback: CallbackQuery):
    await callback.answer()
    await show_carrier_menu(callback.message)

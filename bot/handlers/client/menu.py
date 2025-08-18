from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, CallbackQuery
from aiogram import Router, F
from bot.decorators.access import require_verified_client
from bot.handlers.carrier_company.car_registration.fsm_helpers import (
    deactivate_inline_keyboard,
)
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.handlers.client import crud
from bot.services.google_services.sheets_client import RequestSheetManager

router = Router()
client_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="✍️ Створити заявку"),
            KeyboardButton(text="📋 Мої заявки"),
        ],
        [KeyboardButton(text="📦 Активні перевезення")],
        [KeyboardButton(text="⚙️ Налаштування профілю")],
        [KeyboardButton(text="🆘 Підтримка")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Оберіть опцію",
    one_time_keyboard=False,
)


async def show_client_menu(target: Message | CallbackQuery):
    text = (
        "📁 Ви в головному меню клієнта.\n\n"
        "Скористайтесь кнопками нижче для створення або перегляду заявок."
    )

    if isinstance(target, CallbackQuery):
        await target.answer()

        try:
            await target.message.delete()
        except Exception:
            pass  # якщо повідомлення вже видалено

        await target.message.answer(
            text=text,
            reply_markup=client_menu_keyboard,
            parse_mode="HTML",
        )
    else:
        await target.answer(
            text=text,
            reply_markup=client_menu_keyboard,
            parse_mode="HTML",
        )


@router.callback_query(F.data == "client_menu")
@require_verified_client()
async def handle_menu_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await deactivate_inline_keyboard(callback.message)
    await show_client_menu(callback.message)


# @router.message(F.text == "📋 Мої заявки")
# async def handle_client_requests(message: Message):
#     telegram_id = message.from_user.id
#     sheet_url = await crud.get_sheet_url_by_telegram_id(telegram_id)

#     if not sheet_url:
#         await message.answer("⛔️ У вас ще немає створених заявок.")
#         inline_keyboard = InlineKeyboardMarkup(
#             inline_keyboard=[
#                 [
#                     InlineKeyboardButton(
#                         text="➕ Створити заявку",
#                         callback_data="client_application",
#                     )
#                 ]
#             ]
#         )
#         await message.answer(
#             "🔗 Натисніть кнопку нижче, щоб створити вашу першу заявку:",
#             reply_markup=inline_keyboard,
#         )
#         return

#     inline_keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text="Відкрити мої заявки",
#                     url=sheet_url,
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text="➕ Створити нову заявку",
#                     callback_data="client_application",
#                 ),
#             ],
#         ]
#     )

#     await message.answer(
#         "🔗 Натисніть кнопку нижче, щоб переглянути ваші заявки:",
#         reply_markup=inline_keyboard,
#     )


@router.message(F.text == "📋 Мої заявки")
async def handle_my_requests(message: Message):
    telegram_id = message.from_user.id
    client = await crud.get_client_by_telegram_id(telegram_id)

    if not client.google_sheet_url:
        client = await crud.get_client_by_telegram_id(telegram_id)
        manager = RequestSheetManager()
        sheet_id, sheet_url = manager.create_request_sheet(
            client.full_name, client.email
        )
        await crud.update_client_sheet_by_telegram(telegram_id, sheet_id, sheet_url)

    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Відкрити заявки", url=sheet_url)],
            [
                InlineKeyboardButton(
                    text="✍️ Створити заявку", callback_data="client_application"
                )
            ],
        ]
    )

    await message.answer("🔗 Ваші заявки:", reply_markup=inline_keyboard)

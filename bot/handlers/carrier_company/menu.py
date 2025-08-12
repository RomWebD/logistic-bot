from aiogram import Router, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from aiogram.fsm.context import FSMContext

from aiogram.filters import Command
from bot.decorators.access import require_verified_carrier
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from bot.handlers.carrier_company import crud
from bot.handlers.carrier_company.car_registration.fsm_helpers import (
    deactivate_inline_keyboard,
)

router = Router()


# Обробка натискання текстової кнопки з ReplyKeyboardMarkup
# @router.message(F.text == "🚚 Мої транспортні засоби")
# async def handle_vehicles_button(message: Message):
#     await message.answer(
#         "🔗 Натисніть кнопку нижче, щоб переглянути ваш автопарк:",
#         reply_markup=vehicle_webapp_markup,
#     )
@router.message(F.text == "🚚 Мої транспортні засоби")
async def handle_vehicles_button(message: Message):
    telegram_id = message.from_user.id
    sheet_url = await crud.get_sheet_url_by_telegram_id(telegram_id)

    if not sheet_url:
        await message.answer(
            "⛔️ Немає жодного транспортного засобу, добавте хочаб 1 транспортний засіб, для перегляду автопарку"
        )
        inline_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="➕ Добавити транспорт",
                        callback_data="carrier_add_new_car",
                    ),
                ],
            ]
        )
        await message.answer(
            "🔗 Натисніть кнопку нижче, щоб добавити транспорт:",
            reply_markup=inline_keyboard,
        )
        return

    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Відкрити автопарк",
                    url=sheet_url,
                )
            ],
            [
                InlineKeyboardButton(
                    text="➕ Добавити транспорт",
                    callback_data="carrier_add_new_car",
                ),
            ],
        ]
    )

    await message.answer(
        "🔗 Натисніть кнопку нижче, щоб переглянути ваш автопарк:",
        reply_markup=inline_keyboard,
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


async def show_carrier_menu(target: Message | CallbackQuery):
    text = "📁 Ви в головному меню перевізника.\n\n Будь ласка, скористайтесь кнопками нижче для подальших дій."

    if isinstance(target, CallbackQuery):
        await target.answer()

        try:
            await target.message.delete()
        except Exception:
            pass  # на випадок якщо повідомлення вже видалено
        await target.message.answer(
            reply_markup=carrier_menu_keyboard,
            # text="\u2063",
            text=text,
            parse_mode="HTML",
        )
    else:
        await target.answer(
            text=text,
            # text="\u2063",
            reply_markup=carrier_menu_keyboard,
            parse_mode="HTML",
        )


@router.message(Command("menu"))
@require_verified_carrier()
async def handle_menu_command(message: Message):
    await show_carrier_menu(message)


@router.callback_query(F.data == "menu")
@require_verified_carrier()
async def handle_menu_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await deactivate_inline_keyboard(callback.message)
    await show_carrier_menu(callback.message)

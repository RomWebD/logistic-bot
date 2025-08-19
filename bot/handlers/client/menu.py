from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, CallbackQuery
from aiogram import Router, F
from bot.decorators.access import require_verified_client
from bot.handlers.carrier_company.car_registration.fsm_helpers import (
    deactivate_inline_keyboard,
)
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.handlers.client import crud
from bot.models.client import SheetStatus
from bot.services.celery.task_tracker import is_sheet_job_active
from bot.services.google_services.sheets_client import RequestSheetManager
from bot.services.celery.tasks import ensure_client_request_sheet

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


@router.message(F.text == "/client_menu")
@require_verified_client()
async def handle_menu_command(message: Message, state: FSMContext):
    await state.clear()
    await show_client_menu(message)


@router.callback_query(F.data == "client_menu")
@require_verified_client()
async def handle_menu_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await deactivate_inline_keyboard(callback.message)
    await show_client_menu(callback.message)


@router.message(F.text == "📋 Мої заявки")
@require_verified_client()
async def handle_my_requests(message: Message):
    telegram_id = message.from_user.id
    client = await crud.get_client_by_telegram_id(telegram_id)
    if not client:
        await message.answer("⛔️ Ви ще не зареєстровані як клієнт.")
        return

    total = await crud.count_requests_by_telegram(telegram_id)
    if total == 0:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✍️ Створити заявку", callback_data="client_application"
                    )
                ]
            ]
        )
        await message.answer(
            "У вас ще немає заявок. Створіть першу — і тоді ми автоматично підготуємо Google Sheet.",
            reply_markup=kb,
        )
        return

    # 🔹 Перевірка Redis-локу
    if is_sheet_job_active(telegram_id):
        await message.answer(
            "⏳ Ваш Google Sheet формується, зачекайте кілька секунд..."
        )
        return

    # 🔹 Перевірка статусу у БД
    if client.sheet_status == SheetStatus.READY and client.google_sheet_url:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔗 Мої заявки", url=client.google_sheet_url
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="✍️ Створити нову заявку",
                        callback_data="client_application",
                    )
                ],
            ]
        )
        await message.answer("🔗 Ваші заявки:", reply_markup=kb)
        return

    if client.sheet_status == SheetStatus.FAILED:
        await message.answer(
            "⚠️ Сталася помилка при створенні Google Sheet. Спробуйте ще раз."
        )
        ensure_client_request_sheet.delay(telegram_id)
        return

    # 🔹 Якщо статус NONE або URL відсутній → запускаємо створення
    await message.answer("⏳ Формуємо ваш Google Sheet із заявками...")
    ensure_client_request_sheet.delay(telegram_id)

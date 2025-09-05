# bot/handlers/client/menu.py
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from bot.decorators.access import require_verified
from bot.handlers.carrier_company.car_registration.fsm_helpers import (
    deactivate_inline_keyboard,
)

from bot.repositories.client_repository import ClientRepository
from bot.repositories.google_sheet_repository import GoogleSheetRepository
from bot.repositories.shipment_repository import ShipmentRepository
from bot.models.google_sheets_binding import SheetStatus, OwnerType, SheetType

from bot.services.celery.task_tracker import is_sheet_job_active
from bot.services.celery.tasks import ensure_client_request_sheet
from bot.ui.main_menu import Role

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
            pass
        await target.message.answer(
            text=text, reply_markup=client_menu_keyboard, parse_mode="HTML"
        )
    else:
        await target.answer(
            text=text, reply_markup=client_menu_keyboard, parse_mode="HTML"
        )


@router.message(F.text == "/client_menu")
@require_verified(Role.CLIENT)
async def handle_menu_command(
    message: Message, state: FSMContext, client_repo: ClientRepository
):
    await state.clear()
    await show_client_menu(message)


@router.callback_query(F.data == "client_menu")
@require_verified(Role.CLIENT)
async def handle_menu_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await deactivate_inline_keyboard(callback.message)
    await show_client_menu(callback.message)


@router.message(F.text == "📋 Мої заявки")
@require_verified(Role.CLIENT)
async def handle_my_requests(
    message: Message,
    client_repo: ClientRepository,
    sheet_repo: GoogleSheetRepository,
    shipment_repo: ShipmentRepository,
):
    telegram_id = message.from_user.id

    client = await client_repo.get_by_telegram_id(telegram_id)
    if not client:
        # теоретично не дійде, бо require_verified_client
        await message.answer("⛔️ Ви ще не зареєстровані як клієнт.")
        return

    total = await shipment_repo.count_by_client(telegram_id)
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

    # Redis-лок
    if is_sheet_job_active(telegram_id):
        await message.answer(
            "⏳ Ваш Google Sheet формується, зачекайте кілька секунд..."
        )
        return

    # Спроба знайти готовий binding
    binding = await sheet_repo.get_ready_binding_by_owner_and_type(
        telegram_id=telegram_id,
        owner_type=OwnerType.CLIENT,
        sheet_type=SheetType.REQUESTS,
    )

    if binding and binding.sheet_url:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔗 Мої заявки", url=binding.sheet_url)],
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

    # Перевірка статусу (може бути FAILED / NONE / CREATING)
    binding = await sheet_repo.get_or_create(
        telegram_id=telegram_id,
        owner_type=OwnerType.CLIENT,
        sheet_type=SheetType.REQUESTS,
    )

    if binding.status == SheetStatus.FAILED:
        await message.answer(
            "⚠️ Сталася помилка при створенні Google Sheet. Спробуйте ще раз."
        )
        ensure_client_request_sheet.delay(telegram_id)
        return

    # NONE або CREATING або READY без url → запускаємо створення
    await message.answer("⏳ Формуємо ваш Google Sheet із заявками...")
    ensure_client_request_sheet.delay(telegram_id)

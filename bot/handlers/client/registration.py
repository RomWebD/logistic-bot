# bot/handlers/client/registration.py
from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from bot.schemas.client import (
    ClientRegistrationData,
    validate_full_name_input,
    validate_phone_input,
    validate_email_input,
    validate_company_name_input,
    validate_tax_id_input,
    validate_website_input,
)
from bot.services.client.client_registration import (
    check_existing_client,
    register_new_client,
)
from bot.ui.keyboards import client_main_kb

router = Router()


class RegisterClientFSM(StatesGroup):
    full_name = State()
    phone = State()
    email = State()
    company_name = State()
    tax_id = State()
    address = State()
    website = State()


@router.callback_query(F.data == "role_client")
async def start_client_registration(callback: CallbackQuery, state: FSMContext):
    telegram_id = callback.from_user.id

    if await check_existing_client(telegram_id):
        await callback.message.answer(
            "✅ Ви вже зареєстровані як клієнт.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="📦 Створити заявку",
                            callback_data="client_application",
                        )
                    ]
                ]
            ),
        )
        await callback.answer()
        return

    # ініціалізуємо FSM-дані
    await state.update_data(telegram_id=telegram_id)
    await callback.message.answer("👤 Введіть ваше ПІБ:")
    await state.set_state(RegisterClientFSM.full_name)
    await callback.answer()


@router.message(RegisterClientFSM.full_name)
async def get_full_name(message: Message, state: FSMContext):
    val, err = validate_full_name_input(message.text)
    if err:
        await message.answer(f"❌ {err}\nСпробуйте ще раз:")
        return
    await state.update_data(full_name=val)
    await message.answer("📞 Введіть ваш номер телефону (напр.: +380501234567):")
    await state.set_state(RegisterClientFSM.phone)


@router.message(RegisterClientFSM.phone)
async def get_phone(message: Message, state: FSMContext):
    val, err = validate_phone_input(message.text)
    if err:
        await message.answer(f"❌ {err}\nСпробуйте ще раз:")
        return
    await state.update_data(phone=val)
    await message.answer("📧 Введіть вашу електронну пошту:")
    await state.set_state(RegisterClientFSM.email)


@router.message(RegisterClientFSM.email)
async def get_email(message: Message, state: FSMContext):
    val, err = validate_email_input(message.text)
    if err:
        await message.answer(f"❌ {err}\nСпробуйте ще раз (приклад: name@example.com):")
        return
    await state.update_data(email=val)
    await message.answer(
        "🏢 Введіть назву компанії(наприклад: ТОВ Кронтехно або ФОП Петришин Петро Петрович):"
    )
    await state.set_state(RegisterClientFSM.company_name)


@router.message(RegisterClientFSM.company_name)
async def get_company_name(message: Message, state: FSMContext):
    val, err = validate_company_name_input(message.text)
    if err:
        await message.answer(f"❌ {err}\nСпробуйте ще раз:")
        return
    await state.update_data(company_name=val)
    await message.answer("🆔 Введіть ЄДРПОУ (8 цифр) або ІПН (10 цифр):")
    await state.set_state(RegisterClientFSM.tax_id)


@router.message(RegisterClientFSM.tax_id)
async def get_tax_id(message: Message, state: FSMContext):
    val, err = validate_tax_id_input(message.text)
    if err:
        await message.answer(f"❌ {err}\nСпробуйте ще раз:")
        return
    await state.update_data(tax_id=val)
    await message.answer("📍 Введіть адресу офісу (можна скорочено):")
    await state.set_state(RegisterClientFSM.address)


@router.message(RegisterClientFSM.address)
async def get_address(message: Message, state: FSMContext):
    addr = (message.text or "").strip()
    await state.update_data(address=addr if addr else None)
    await message.answer("🔗 Введіть сайт компанії або '-' якщо немає:")
    await state.set_state(RegisterClientFSM.website)


@router.message(RegisterClientFSM.website)
async def finalize_registration(message: Message, state: FSMContext):
    website, err = validate_website_input(message.text)
    if err:
        await message.answer(
            f"❌ {err}\nСпробуйте ще раз або введіть '-' якщо немає сайту:"
        )
        return

    data = await state.get_data()
    telegram_id = data["telegram_id"]

    # збираємо фінальні нормалізовані значення
    payload = ClientRegistrationData(
        telegram_id=telegram_id,
        full_name=data["full_name"],
        company_name=data["company_name"],
        tax_id=data["tax_id"],
        phone=data["phone"],
        email=data["email"],
        address=data.get("address"),
        website=website,  # None або валідний URL
    )

    success = await register_new_client(payload)
    if not success:
        await message.answer("⚠️ Клієнт з таким номером або поштою вже існує.")
    else:
        await message.answer(
            "✅ Реєстрація клієнта успішна!\n"
            "⚠️ Ви ще не верифіковані. Зачекайте підтвердження або зверніться до адміністратора.",
            reply_markup=client_main_kb(
                is_verified=False
            ),  # ⬅️ без кнопки створення заявки
        )
    await state.clear()

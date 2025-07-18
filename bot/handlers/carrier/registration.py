# bot/handlers/registration.py

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from bot.models import Carrier
from bot.database.database import async_session
from aiogram.types import CallbackQuery

router = Router()


# Оголошуємо стани
class RegisterCarrier(StatesGroup):
    full_name = State()
    phone = State()
    route = State()


# @router.message()
# async def debug_all_messages(message: Message):
#     print("🔥 DEBUG MESSAGE TEXT:", repr(message.text))
#     await message.answer(
#         f"🔍 Ви написали: <code>{message.text}</code>", parse_mode="HTML"
#     )


@router.callback_query(F.data == "role_carrier")
async def handle_role_carrier(callback: CallbackQuery, state: FSMContext):
    print("start")
    await callback.message.answer(
        "👋 Розпочнемо реєстрацію перевізника.\nВведіть ваше ПІБ:"
    )
    await state.set_state(RegisterCarrier.full_name)
    await callback.answer()


# Зберігаємо ПІБ
@router.message(RegisterCarrier.full_name)
async def get_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("📱 Введіть ваш номер телефону:")
    await state.set_state(RegisterCarrier.phone)


# Зберігаємо телефон
@router.message(RegisterCarrier.phone)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("🧭 Введіть маршрут (наприклад: Київ → Львів):")
    await state.set_state(RegisterCarrier.route)


# Зберігаємо маршрут і реєструємо
@router.message(RegisterCarrier.route)
async def finish_registration(message: Message, state: FSMContext):
    data = await state.get_data()
    telegram_id = message.from_user.id

    async with async_session() as session:
        session.add(
            Carrier(
                telegram_id=telegram_id,
                full_name=data["full_name"],
                phone=data["phone"],
                route=message.text,
            )
        )
        await session.commit()

    await message.answer("✅ Ви успішно зареєстровані як перевізник!")
    await state.clear()

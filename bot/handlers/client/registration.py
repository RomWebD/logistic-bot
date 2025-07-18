# bot/handlers/client/registration.py

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from bot.database.database import async_session
from bot.models.client import Client
from sqlalchemy import select
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()


class RegisterClient(StatesGroup):
    full_name = State()
    phone = State()


@router.callback_query(F.data == "role_client")
async def start_client_registration(callback: CallbackQuery, state: FSMContext):
    telegram_id = callback.from_user.id

    async with async_session() as session:
        existing = await session.scalar(
            select(Client).where(Client.telegram_id == telegram_id)
        )

    if existing:
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

    await callback.message.answer(
        "📦 Ви обрали роль *Клієнта*.\n\n"
        "Перед тим, як створювати заявки, потрібно пройти коротку реєстрацію.\n\n"
        "👤 Введіть ваше ПІБ:",
        parse_mode="Markdown",
    )
    await state.set_state(RegisterClient.full_name)
    await callback.answer()


@router.message(RegisterClient.full_name)
async def get_client_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("📱 Введіть номер телефону:")
    await state.set_state(RegisterClient.phone)


@router.message(RegisterClient.phone)
async def get_client_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    telegram_id = message.from_user.id

    async with async_session() as session:
        # Перевірка на існуючого клієнта
        existing = await session.scalar(
            select(Client).where(Client.telegram_id == telegram_id)
        )
        if existing:
            await message.answer("🔁 Ви вже зареєстровані як клієнт.")
        else:
            session.add(
                Client(
                    telegram_id=telegram_id,
                    full_name=data["full_name"],
                    phone=message.text,
                )
            )
            await session.commit()
            await message.answer(
                "✅ Реєстрація клієнта успішна!",
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
    await state.clear()

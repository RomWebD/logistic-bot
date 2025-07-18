# bot/handlers/client/application.py

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from bot.database.database import async_session
from bot.models.shipment_request import Shipment_request
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()


class ClientApplicationFSM(StatesGroup):
    route = State()
    date = State()
    cargo_type = State()
    volume = State()
    weight = State()
    loading = State()
    unloading = State()
    price = State()


@router.callback_query(F.data == "client_application")
async def start_client_application(callback: CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Так", callback_data="confirm_start_application"
                ),
                InlineKeyboardButton(text="❌ Ні", callback_data="cancel_application"),
            ]
        ]
    )
    await callback.message.answer(
        "📝 Бажаєте створити нову заявку на перевезення?", reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_start_application")
async def confirm_start_application(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📍 Введіть маршрут (наприклад: Київ → Львів):")
    await state.set_state(ClientApplicationFSM.route)
    await callback.answer()


@router.message(ClientApplicationFSM.route)
async def get_route(message: Message, state: FSMContext):
    await state.update_data(route=message.text)
    await message.answer("📅 Введіть дату подачі (наприклад: 20 липня до 10:00):")
    await state.set_state(ClientApplicationFSM.date)


@router.message(ClientApplicationFSM.date)
async def get_date(message: Message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.answer(
        "📦 Введіть тип вантажу(наприклад, Побутова техніка, упакована на палетах):"
    )
    await state.set_state(ClientApplicationFSM.cargo_type)


@router.message(ClientApplicationFSM.cargo_type)
async def get_cargo_type(message: Message, state: FSMContext):
    await state.update_data(cargo_type=message.text)
    await message.answer("📦 Введіть обʼєм (наприклад: 6 палет):")
    await state.set_state(ClientApplicationFSM.volume)


@router.message(ClientApplicationFSM.volume)
async def get_volume(message: Message, state: FSMContext):
    await state.update_data(volume=message.text)
    await message.answer("⚖️ Введіть вагу (наприклад: 2.2 т):")
    await state.set_state(ClientApplicationFSM.weight)


@router.message(ClientApplicationFSM.weight)
async def get_weight(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await message.answer("📥 Як буде завантаження (наприклад: рокла, рампа):")
    await state.set_state(ClientApplicationFSM.loading)


@router.message(ClientApplicationFSM.loading)
async def get_loading(message: Message, state: FSMContext):
    await state.update_data(loading=message.text)
    await message.answer("📤 Як буде вивантаження (наприклад: ручне):")
    await state.set_state(ClientApplicationFSM.unloading)


@router.message(ClientApplicationFSM.unloading)
async def get_unloading(message: Message, state: FSMContext):
    await state.update_data(unloading=message.text)
    await message.answer("💰 Введіть бажану ціну (наприклад: 8000 грн):")
    await state.set_state(ClientApplicationFSM.price)


@router.message(ClientApplicationFSM.price)
async def finish_application(message: Message, state: FSMContext):
    data = await state.get_data()
    telegram_id = message.from_user.id
    price = message.text.strip()

    new_request = Shipment_request(
        client_telegram_id=telegram_id,
        route=data["route"],
        date=data["date"],
        cargo_type=data["cargo_type"],
        volume=data["volume"],
        weight=data["weight"],
        loading=data["loading"],
        unloading=data["unloading"],
        price=price,
    )

    async with async_session() as session:
        session.add(new_request)
        await session.commit()
        await session.refresh(new_request)

    await message.answer(
        f"""📦 <b>Нова заявка на перевезення:</b>
Маршрут: {data["route"]}
Дата подачі: {data["date"]}
Тип вантажу: {data["cargo_type"]}
Обʼєм: {data["volume"]}
Орієнтовна вага: {data["weight"]}
Завантаження: {data["loading"]}
Вивантаження: {data["unloading"]}
Ціна: {price} грн""",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Прийняти рейс",
                        callback_data=f"accept_{new_request.id}",
                    ),
                    InlineKeyboardButton(
                        text="❌ Відмовитись",
                        callback_data=f"decline_{new_request.id}",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="💬 Запропонувати іншу ставку",
                        callback_data=f"negotiate_{new_request.id}",
                    )
                ],
            ]
        ),
        parse_mode="HTML",
    )

    await state.clear()


@router.callback_query(F.data == "cancel_application")
async def cancel_application(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "🚫 Заявку скасовано. Якщо передумаєте — просто натисніть знову кнопку ✍️ Створити заявку."
    )
    await state.clear()
    await callback.answer()

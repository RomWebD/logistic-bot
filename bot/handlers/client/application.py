# bot/handlers/client/application.py

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from bot.database.database import async_session
from bot.models.shipment_request import Shipment_request
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.services.notifier import notify_carriers

router = Router()


class ClientApplicationFSM(StatesGroup):
    from_city = State()
    to_city = State()
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
    await callback.message.answer(
        "🚚 Звідки потрібно забрати вантаж?\n\nВведіть місто відправлення (наприклад: Київ):"
    )
    await state.set_state(ClientApplicationFSM.from_city)
    await callback.answer()


@router.message(ClientApplicationFSM.from_city)
async def get_from_route(message: Message, state: FSMContext):
    await state.update_data(from_city=message.text)
    await message.answer(
        "🏁 Куди потрібно доставити вантаж?\n\nВведіть місто призначення (наприклад: Львів):"
    )
    await state.set_state(ClientApplicationFSM.to_city)


@router.message(ClientApplicationFSM.to_city)
async def get_to_route(message: Message, state: FSMContext):
    await state.update_data(to_city=message.text)
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
    await state.update_data(price=message.text.strip())
    data = await state.get_data()

    await message.answer(
        f"""📦 <b>Перевірте дані заявки:</b>
Маршрут: {data["from_city"]} → {data["to_city"]}
Дата подачі: {data["date"]}
Тип вантажу: {data["cargo_type"]}
Обʼєм: {data["volume"]}
Орієнтовна вага: {data["weight"]}
Завантаження: {data["loading"]}
Вивантаження: {data["unloading"]}
Ціна: {data["price"]} грн

Все вірно?""",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Підтвердити заявку", callback_data="confirm_shipment"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❌ Скасувати", callback_data="cancel_shipment"
                    )
                ],
            ]
        ),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "confirm_shipment")
async def confirm_shipment(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    telegram_id = callback.from_user.id
    new_request = Shipment_request(
        client_telegram_id=telegram_id,
        from_city=data["from_city"],
        to_city=data["to_city"],
        date=data["date"],
        date_text=data["date"],
        cargo_type=data["cargo_type"],
        volume=data["volume"],
        weight=data["weight"],
        loading=data["loading"],
        unloading=data["unloading"],
        price=data["price"],
    )

    async with async_session() as session:
        session.add(new_request)
        await session.commit()
        await session.refresh(new_request)
        await callback.message.edit_text("✅ Заявку створено успішно!")

    #     await message.answer(
    #         f"""📦 <b>Нова заявка на перевезення:</b>
    # Маршрут: {data["route"]}
    # Дата подачі: {data["date"]}
    # Тип вантажу: {data["cargo_type"]}
    # Обʼєм: {data["volume"]}
    # Орієнтовна вага: {data["weight"]}
    # Завантаження: {data["loading"]}
    # Вивантаження: {data["unloading"]}
    # Ціна: {price} грн""",
    # reply_markup=InlineKeyboardMarkup(
    #     inline_keyboard=[
    #         [
    #             InlineKeyboardButton(
    #                 text="✅ Прийняти рейс",
    #                 callback_data=f"accept_{new_request.id}",
    #             ),
    #             InlineKeyboardButton(
    #                 text="❌ Відмовитись",
    #                 callback_data=f"decline_{new_request.id}",
    #             ),
    #         ],
    #         [
    #             InlineKeyboardButton(
    #                 text="💬 Запропонувати іншу ставку",
    #                 callback_data=f"negotiate_{new_request.id}",
    #             )
    #         ],
    #     ]
    # ),
    #     parse_mode="HTML",
    # )

    await notify_carriers(bot=callback.bot, request=new_request)

    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "cancel_application")
async def cancel_application(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "🚫 Заявку скасовано. Якщо передумаєте — просто натисніть знову кнопку ✍️ Створити заявку."
    )
    await state.clear()
    await callback.answer()

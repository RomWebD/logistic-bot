from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from .fsm import get_progress_bar, RegisterCar

router = Router()


async def show_summary(message, state: FSMContext):
    data = await state.get_data()
    summary = (
        f"🚚 **Перевірте введені дані:**\n"
        f"Тип: {data.get('car_type') or '-'}\n"
        f"Номер(и): {data.get('plate_number') or '-'}\n"
        f"Вантажопідйомність: {data.get('weight_capacity') or '-'}\n"
        f"Обʼєм: {data.get('volume') or '-'}\n"
        f"Завантаження: {', '.join(data.get('loading_type') or [])}\n"
        f"Водій: {data.get('driver_fullname') or '-'}\n"
        f"Телефон: {data.get('driver_phone') or '-'}\n" + get_progress_bar(data)
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Зберегти", callback_data="car_save"),
                InlineKeyboardButton(text="✏️ Редагувати", callback_data="car_edit"),
            ],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="car_back")],
        ]
    )

    await message.answer(summary, reply_markup=keyboard)
    await message.answer(summary, reply_markup=None)


@router.callback_query(F.data == "car_save")
async def save_car(callback: CallbackQuery, state: FSMContext):
    # Тут буде логіка збереження у БД, якщо потрібно
    await callback.message.edit_text("✅ Транспорт успішно додано!", reply_markup=None)
    await state.clear()


@router.callback_query(F.data == "car_back")
async def go_back(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("⬅️ Введіть номер телефону водія ще раз:")
    await state.set_state(RegisterCar.driver_phone)

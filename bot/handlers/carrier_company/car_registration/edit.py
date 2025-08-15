# bot/handlers/carrier_company/car_registration/edit.py

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from bot.handlers.carrier_company.car_registration.fsm_helpers import (
    go_to_edit_step,
    FIELD_LABELS,
)

router = Router()

EDIT_CALLBACK_PREFIX = "edit_"


@router.callback_query(F.data == "car_edit")
async def edit_car(callback: CallbackQuery, state: FSMContext):
    # Генеруємо кнопки для вибору кількох полів

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚛 Тип транспорту", callback_data="edit_car_type"
                ),
                InlineKeyboardButton(
                    text="🔢 Номер(и) авто", callback_data="edit_plate_number"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⚖️ Вантажопідйомність", callback_data="edit_weight_capacity"
                ),
                InlineKeyboardButton(text="📦 Обʼєм", callback_data="edit_volume"),
            ],
            [
                InlineKeyboardButton(
                    text="📥 Спосіб завантаження", callback_data="edit_loading_type"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👤 ПІБ водія", callback_data="edit_driver_fullname"
                ),
                InlineKeyboardButton(
                    text="📞 Телефон водія", callback_data="edit_driver_phone"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✅ Почати редагування", callback_data="edit_start"
                )
            ],
        ]
    )

    await state.update_data(edit_queue=[])  # очищаємо чергу перед вибором
    await callback.message.edit_text(
        "🔁 Оберіть поля, які хочете змінити:", reply_markup=keyboard
    )


@router.callback_query(F.data == "edit_start")
async def begin_edit(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    queue = data.get("edit_queue", [])

    if not queue:
        await callback.answer("Оберіть хоча б одне поле")
        return

    # Починаємо з першого поля
    first_field = queue[0]
    await go_to_edit_step(state, first_field, callback.message)


@router.callback_query(F.data.startswith(EDIT_CALLBACK_PREFIX))
async def select_field_for_edit(callback: CallbackQuery, state: FSMContext):
    field = callback.data.removeprefix(EDIT_CALLBACK_PREFIX)
    data = await state.get_data()
    queue = data.get("edit_queue", [])

    if field not in queue:
        queue.append(field)
        await callback.answer(f"✅ Додано: {FIELD_LABELS.get(field, field)}")
    else:
        queue.remove(field)
        await callback.answer(f"❌ Видалено: {FIELD_LABELS.get(field, field)}")

    await state.update_data(edit_queue=queue)


async def handle_editing_step(state: FSMContext, field: str, value, message):
    await state.update_data({field: value})
    data = await state.get_data()
    queue = data.get("edit_queue", [])
    queue.remove(field)

    await state.update_data(edit_queue=queue)

    if queue:
        next_field = queue[0]
        await go_to_edit_step(state, next_field, message)
    else:
        from .summary import show_summary

        await show_summary(message, state)

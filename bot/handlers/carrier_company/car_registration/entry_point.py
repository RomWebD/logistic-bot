from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from .fsm import RegisterCar
from .fsm_helpers import get_car_type_keyboard, go_to_next_edit_step, go_to_next_step

router = Router()


@router.callback_query(F.data == "carrier_add_new_car")
async def start_register_car(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "🚛 Оберіть тип транспорту:", reply_markup=get_car_type_keyboard()
    )
    await state.set_state(RegisterCar.car_type)


@router.callback_query(RegisterCar.car_type, F.data.startswith("type_"))
async def set_vehicle_type(callback: CallbackQuery, state: FSMContext):
    value = callback.data.removeprefix("type_")
    if value == "other":
        await callback.message.answer("Введіть тип транспорту вручну:")
    else:
        await state.update_data(car_type=value)
        data = await state.get_data()
        if "edit_queue" in data:
            await go_to_next_edit_step(state, "car_type", callback.message)
        else:
            await go_to_next_step(state, "car_type", callback.message)


@router.message(RegisterCar.car_type)
async def set_custom_type(message: Message, state: FSMContext):
    await state.update_data(car_type=message.text)
    data = await state.get_data()
    if "edit_queue" in data:
        await go_to_next_edit_step(state, "car_type", message)
    else:
        await go_to_next_step(state, "car_type", message)

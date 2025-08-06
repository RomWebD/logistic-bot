from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.handlers.carrier_company.car_registration.fsm_helpers import (
    go_to_next_step,
    go_to_next_edit_step,
)

from .fsm import RegisterCar

router = Router()


@router.message(RegisterCar.plate_number)
async def set_plate(message: Message, state: FSMContext):
    await state.update_data(plate_number=message.text)
    data = await state.get_data()
    if "edit_queue" in data:
        await go_to_next_edit_step(state, "plate_number", message)
    else:
        await go_to_next_step(state, "plate_number", message)


@router.message(RegisterCar.weight_capacity)
async def set_capacity(message: Message, state: FSMContext):
    await state.update_data(weight_capacity=message.text)
    data = await state.get_data()
    if "edit_queue" in data:
        await go_to_next_edit_step(state, "weight_capacity", message)
    else:
        await go_to_next_step(state, "weight_capacity", message)


@router.message(RegisterCar.volume)
async def set_volume(message: Message, state: FSMContext):
    await state.update_data(volume=message.text)
    data = await state.get_data()
    if "edit_queue" in data:
        await go_to_next_edit_step(state, "volume", message)
    else:
        await go_to_next_step(state, "volume", message)


@router.message(RegisterCar.driver_fullname)
async def set_driver_name(message: Message, state: FSMContext):
    await state.update_data(driver_fullname=message.text)
    data = await state.get_data()
    if "edit_queue" in data:
        await go_to_next_edit_step(state, "driver_fullname", message)
    else:
        await go_to_next_step(state, "driver_fullname", message)


@router.message(RegisterCar.driver_phone)
async def finish(message: Message, state: FSMContext):
    await state.update_data(driver_phone=message.text)
    data = await state.get_data()
    if "edit_queue" in data:
        await go_to_next_edit_step(state, "driver_phone", message)
    else:
        await go_to_next_step(state, "driver_phone", message)


@router.callback_query(F.data.startswith("skip_"))
async def skip_field(callback: CallbackQuery, state: FSMContext):
    field = callback.data.replace("skip_", "")
    await state.update_data({field: None})
    data = await state.get_data()
    if "edit_queue" in data:
        await go_to_next_edit_step(state, field, callback.message)
    else:
        await go_to_next_step(state, field, callback.message)

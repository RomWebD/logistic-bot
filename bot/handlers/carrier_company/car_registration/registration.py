# bot/handlers/vehicle/registration_form.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from bot.forms.car_registration import VehicleRegistrationForm
from bot.forms.aiogram_adapter import FormRouter
from bot.decorators.access import require_verified
from bot.ui.main_menu import Role

router = Router()

vehicle_form_router = FormRouter(VehicleRegistrationForm(), prefix="vehicle")
router.include_router(vehicle_form_router.router)


# Точка входу з меню перевізника
@router.callback_query(F.data == "carrier_add_vehicle")
@require_verified(Role.CARRIER)
async def start_vehicle_registration(cb: CallbackQuery, state: FSMContext):
    await state.update_data(tg_id=cb.from_user.id)
    await cb.message.answer(
        "🚚 Додати транспорт?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Почати", callback_data="vehicle:form_start"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❌ Скасувати", callback_data="vehicle:form_cancel"
                    )
                ],
            ]
        ),
    )
    await cb.answer()

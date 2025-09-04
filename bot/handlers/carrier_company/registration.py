# bot/handlers/carrier/registration_form.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from bot.forms.carrier_registration import CarrierRegistrationForm
from bot.forms.aiogram_adapter import FormRouter
from bot.services.carrier.registration import CarrierRegistrationService
from bot.services.bot_commands import set_verified_carrier_menu  # якщо треба
# from bot.ui.keyboards import carrier_main_kb  # якщо є меню перевізника

router = Router()
carrier_form_router = FormRouter(CarrierRegistrationForm(), prefix="carrier")
router.include_router(carrier_form_router.router)


@router.callback_query(F.data == "role_carrier")
async def start_carrier_registration(callback: CallbackQuery, state: FSMContext):
    tg_id = callback.from_user.id

    # ✅ Гард від повторної реєстрації
    async with CarrierRegistrationService() as svc:
        existing = await svc.get_by_tg(tg_id)
        if existing:
            await callback.message.answer(
                "⚠️ Ви вже зареєстровані як перевізник.",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📂 Перейти до меню", callback_data="menu"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text="❌ Видалити профіль",
                                callback_data="delete_carrier_profile",
                            )
                        ],
                    ]
                ),
            )
            await callback.answer()
            return

    await state.update_data(tg_id=tg_id)
    await callback.message.answer(
        "🚚 Почнемо реєстрацію перевізника?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Почати", callback_data="carrier:form_start"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❌ Скасувати", callback_data="carrier:form_scancel"
                    )
                ],
            ]
        ),
    )
    await callback.answer()

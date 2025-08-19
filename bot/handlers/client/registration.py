# bot/handlers/client/registration_form.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from bot.forms.client_registration import ClientRegistrationForm
from bot.forms.aiogram_adapter import FormRouter

router = Router()

client_form = ClientRegistrationForm()
client_form_router = FormRouter(client_form)
router.include_router(client_form_router.router)


@router.callback_query(F.data == "role_client")
async def start_client_registration(callback: CallbackQuery, state: FSMContext):
    await state.update_data(tg_id=callback.from_user.id)
    await callback.message.answer(
        "🧑‍💼 Почнемо реєстрацію клієнта?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Почати", callback_data="form_start")],
                [InlineKeyboardButton(text="❌ Скасувати", callback_data="form_cancel")],
            ]
        ),
    )
    await callback.answer()

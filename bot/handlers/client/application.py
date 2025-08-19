from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from bot.forms.shipment_request import ShipmentRequestForm
from bot.forms.aiogram_adapter import FormRouter

router = Router()

# створюємо форму та підключаємо її роутер
shipment_form = ShipmentRequestForm()
shipment_form_router = FormRouter(shipment_form)
router.include_router(shipment_form_router.router)


@router.callback_query(F.data == "client_application")
async def start_client_application(callback: CallbackQuery, state: FSMContext):
    """
    Точка входу:
    - кладемо tg_id у state (щоб on_submit знав, хто юзер)
    - показуємо кнопку "Почати" (використає FormRouter → form_start)
    """
    await state.update_data(tg_id=callback.from_user.id)

    await callback.message.answer(
        "📝 Бажаєте створити нову заявку на перевезення?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Почати", callback_data="form_start")],
                [
                    InlineKeyboardButton(
                        text="❌ Скасувати", callback_data="form_cancel"
                    )
                ],
            ]
        ),
    )
    await callback.answer()


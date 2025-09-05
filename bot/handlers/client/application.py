# bot/handlers/client/request_start.py
from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext

from bot.decorators.access import require_verified
from bot.forms.aiogram_adapter import FormRouter
from bot.forms.shipment_request import ShipmentRequestForm
from bot.repositories.client_repository import ClientRepository
from bot.ui.main_menu import Role

router = Router()
client_form_router = FormRouter(ShipmentRequestForm(), prefix="request")

router.include_router(client_form_router.router)


MENU_CREATE_REQUEST = "✍️ Створити заявку"


def build_request_start_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Почати", callback_data="request:form_start"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Скасувати", callback_data="request:form_cancel"
                )
            ],
        ]
    )


async def send_request_start_prompt(send_to, tg_id: int):
    # send_to: Message або CallbackQuery.message
    await send_to.answer(
        "📝 Бажаєте створити нову заявку на перевезення?",
        reply_markup=build_request_start_kb(),
    )


# 1) Інлайн варіант (callback)
@router.callback_query(F.data == "client_application")
@require_verified(Role.CLIENT)
async def start_client_application_cb(
    callback: CallbackQuery, state: FSMContext, client_repo: ClientRepository
):
    await state.update_data(tg_id=callback.from_user.id)
    await send_request_start_prompt(callback.message, callback.from_user.id)
    await callback.answer()


@router.message(F.text == MENU_CREATE_REQUEST)
@require_verified(Role.CLIENT)
async def start_client_application_msg(
    message: Message, state: FSMContext, client_repo: ClientRepository
):
    await state.update_data(tg_id=message.from_user.id)
    await send_request_start_prompt(message, message.from_user.id)

# bot/handlers/client/verification.py
from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BotCommand,
    BotCommandScopeChat,
)
from aiogram.exceptions import TelegramBadRequest
from bot.services.client.registration import ClientRegistrationService
from bot.handlers.client import crud
from bot.ui.keyboards import client_main_kb
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()


@router.callback_query(F.data == "client_check_status")
async def handle_client_check_status(callback: CallbackQuery, session: AsyncSession):
    await callback.answer("Перевіряю статус…")
    tg_id = callback.from_user.id
    service = ClientRegistrationService(session=session)
    client = await service.check_existing(tg_id)
    if not client:
        # користувача немає у БД — запропонувати зареєструватись
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📦 Я клієнт", callback_data="role_client")]
            ]
        )
        await _safe_edit_or_send(
            callback,
            text="⛔️ Вас ще не знайдено в системі. Будь ласка, пройдіть реєстрацію.",
            reply_markup=kb,
        )
        return

    if client.is_verified:
        # ✅ верифікований — оновити клавіатуру і текст
        success_text = (
            "✅ Ваш профіль верифіковано!\n"
            "Можете створити першу заявку або перейти до профілю."
        )

        # (опційно) встановити персональні команди тільки для цього чату
        try:
            await callback.bot.set_my_commands(
                commands=[
                    BotCommand(command="client_menu", description="Меню клієнта"),
                ],
                scope=BotCommandScopeChat(chat_id=tg_id),
            )
        except Exception:
            # якщо не критично — ігноруємо
            pass

        await _safe_edit_or_send(
            callback,
            text=success_text,
            reply_markup=client_main_kb(is_verified=True),
        )
    else:
        # ⏳ ще очікує — залишаємо обмежене меню
        pending_text = (
            "⏳ Ваш профіль ще проходить верифікацію.\n"
            "Спробуйте пізніше або зверніться до адміністратора."
        )

        # (опційно) прибрати команди, якщо були (щоб меню не лишалось після перезапуску)
        try:
            await callback.bot.delete_my_commands(
                scope=BotCommandScopeChat(chat_id=tg_id)
            )
        except Exception:
            pass

        await _safe_edit_or_send(
            callback,
            text=pending_text,
            reply_markup=client_main_kb(is_verified=False),
        )


async def _safe_edit_or_send(
    callback: CallbackQuery, text: str, reply_markup: InlineKeyboardMarkup
):
    """
    Акуратно оновлює існуюче повідомлення (тільки текст/клаву).
    Якщо Telegram не дозволяє редагування (видалено/змінено), шле нове.
    """
    try:
        # Спроба оновити текст і клаву в одному виклику
        await callback.message.edit_text(text=text, reply_markup=reply_markup)
    except TelegramBadRequest:
        try:
            # Якщо не вдалося змінити текст — хоча б клаву
            await callback.message.edit_reply_markup(reply_markup=reply_markup)
            await callback.message.answer(text, reply_markup=None)
        except TelegramBadRequest:
            # Якщо і клаву не можна — надсилаємо нове повідомлення
            await callback.message.answer(text, reply_markup=reply_markup)

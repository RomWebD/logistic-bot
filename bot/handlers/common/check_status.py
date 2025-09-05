# bot/handlers/common/check_status.py
from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BotCommand,
    BotCommandScopeChat,
)
from bot.ui.main_menu import Role, main_menu_kb
from bot.services.client.registration import ClientRegistrationService
from bot.services.carrier.registration import CarrierRegistrationService

router = Router()


@router.callback_query(F.data.regexp(r"^(client|carrier)_check_status$"))
async def handle_check_status(callback: CallbackQuery, session: "AsyncSession"):
    await callback.answer("Перевіряю статус…")
    tg_id = callback.from_user.id
    role = Role(callback.data.split("_", 1)[0])

    if role == Role.CLIENT:
        async with ClientRegistrationService(session=session) as svc:
            client = await svc.get_by_tg(tg_id)
        if not client:
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="📦 Я клієнт", callback_data="role_client"
                        )
                    ]
                ]
            )
            await callback.message.edit_text(
                "⛔️ Вас ще не знайдено в системі. Будь ласка, пройдіть реєстрацію.",
                reply_markup=kb,
            )
            return
        if client.is_verified:
            try:
                await callback.bot.set_my_commands(
                    commands=[
                        BotCommand(command="client_menu", description="Меню клієнта")
                    ],
                    scope=BotCommandScopeChat(chat_id=tg_id),
                )
            except Exception:
                pass
            await callback.message.edit_text(
                "✅ Ваш профіль верифіковано!\nМожете створити першу заявку або перейти до профілю.",
                reply_markup=main_menu_kb(Role.CLIENT, is_verified=True),
            )
        else:
            try:
                await callback.bot.delete_my_commands(
                    scope=BotCommandScopeChat(chat_id=tg_id)
                )
            except Exception:
                pass
            await callback.message.edit_text(
                "⏳ Ваш профіль ще проходить верифікацію.",
                reply_markup=main_menu_kb(Role.CLIENT, is_verified=False),
            )
    else:
        async with CarrierRegistrationService(session=session) as svc:
            carrier = await svc.get_by_tg(tg_id)
        if not carrier:
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🚚 Я перевізник", callback_data="role_carrier"
                        )
                    ]
                ]
            )
            await callback.message.edit_text(
                "⛔️ Вас ще не знайдено в системі. Будь ласка, пройдіть реєстрацію.",
                reply_markup=kb,
            )
            return
        if carrier.is_verified:
            try:
                await callback.bot.set_my_commands(
                    commands=[
                        BotCommand(
                            command="carrier_menu", description="Меню перевізника"
                        )
                    ],
                    scope=BotCommandScopeChat(chat_id=tg_id),
                )
            except Exception:
                pass
            await callback.message.edit_text(
                "✅ Профіль перевізника верифіковано!",
                reply_markup=main_menu_kb(Role.CARRIER, is_verified=True),
            )
        else:
            try:
                await callback.bot.delete_my_commands(
                    scope=BotCommandScopeChat(chat_id=tg_id)
                )
            except Exception:
                pass
            await callback.message.edit_text(
                "⏳ Профіль Все ще проходить верифікацію.",
                reply_markup=main_menu_kb(Role.CARRIER, is_verified=False),
            )

# bot/decorators/access.py
from functools import wraps
from aiogram.types import Message, CallbackQuery, BotCommandScopeChat
from bot.services.verification import CarrierStatus, get_carrier_status
from typing import Union

from bot.services.client.verification_client import ClientStatus, get_client_status


def require_verified_carrier():
    def decorator(func):
        @wraps(func)
        async def wrapper(message: Message, *args, **kwargs):
            telegram_id = message.from_user.id
            status = await get_carrier_status(telegram_id)

            if status == CarrierStatus.VERIFIED:
                return await func(message, *args, **kwargs)

            elif status == CarrierStatus.NOT_VERIFIED:
                await message.answer(
                    "⚠️ Ви ще не верифіковані. Зачекайте підтвердження або зверніться до адміністратора."
                )
                return

            elif status == CarrierStatus.NOT_REGISTERED:
                # 🧼 Відчищаємо меню
                await message.bot.delete_my_commands(
                    scope=BotCommandScopeChat(chat_id=telegram_id)
                )
                await message.answer(
                    "❌ Вас не знайдено у системі. Будь ласка, почніть з /start."
                )
                return

        return wrapper

    return decorator


def require_verified_client():
    def decorator(func):
        @wraps(func)
        async def wrapper(event: Union[Message, CallbackQuery], *args, **kwargs):
            user = (
                event.from_user if isinstance(event, CallbackQuery) else event.from_user
            )
            chat_id = user.id
            status = await get_client_status(chat_id)

            if status == ClientStatus.VERIFIED:
                return await func(event, *args, **kwargs)

            if status == ClientStatus.NOT_VERIFIED:
                # Відповідь коректно і для Message, і для CallbackQuery
                if isinstance(event, CallbackQuery):
                    await event.message.answer(
                        "⚠️ Ви ще не верифіковані. Зачекайте підтвердження або зверніться до адміністратора."
                    )
                    await event.answer()
                else:
                    await event.answer(
                        "⚠️ Ви ще не верифіковані. Зачекайте підтвердження або зверніться до адміністратора."
                    )
                return

            # NOT_REGISTERED
            if isinstance(event, CallbackQuery):
                await event.message.bot.delete_my_commands(
                    scope=BotCommandScopeChat(chat_id=chat_id)
                )
                await event.message.answer(
                    "❌ Вас не знайдено у системі. Будь ласка, почніть з /start."
                )
                await event.answer()
            else:
                await event.bot.delete_my_commands(
                    scope=BotCommandScopeChat(chat_id=chat_id)
                )
                await event.answer(
                    "❌ Вас не знайдено у системі. Будь ласка, почніть з /start."
                )

        return wrapper

    return decorator

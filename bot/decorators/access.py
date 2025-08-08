# bot/decorators/access.py
from functools import wraps
from aiogram.types import Message
from bot.services.verification import CarrierStatus, get_carrier_status

from aiogram.types import BotCommandScopeChat


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

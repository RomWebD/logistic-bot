# bot/decorators/access.py
from functools import wraps
from aiogram.types import Message
from bot.services.verification import is_verified_carrier

def require_verified_carrier():
    def decorator(func):
        @wraps(func)
        async def wrapper(message: Message, *args, **kwargs):
            telegram_id = message.from_user.id
            if await is_verified_carrier(telegram_id):
                return await func(message, *args, **kwargs)
            else:
                await message.answer("❌ У вас немає доступу до цієї команди. Ви ще не верифіковані")
                return
        return wrapper
    return decorator

# bot/access/guards.py
from __future__ import annotations
from functools import wraps
from typing import Union, Callable, Awaitable, Type
from aiogram.types import Message, CallbackQuery, BotCommandScopeChat
from bot.ui.main_menu import main_menu_kb, Role
from bot.services.client.registration import ClientRegistrationService
from bot.services.carrier.registration import CarrierRegistrationService

Event = Union[Message, CallbackQuery]

_SERVICE_MAP: dict[Role, Type] = {
    Role.CLIENT: ClientRegistrationService,
    Role.CARRIER: CarrierRegistrationService,
}


async def _send(event: Event, text: str, *, reply_markup=None):
    if isinstance(event, CallbackQuery):
        await event.message.answer(text, reply_markup=reply_markup)
        await event.answer()
    else:
        await event.answer(text, reply_markup=reply_markup)


def require_verified(role: Role):
    """
    Перевірка:
      - якщо запису немає → просимо /start
      - якщо не верифікований → показуємо рольове меню з 'Перевірити статус'
      - якщо верифікований → пропускаємо
    Працює і для Message, і для CallbackQuery.
    Очікує, що у хендлер буде передано `session` (твій middleware вже це робить).
    """
    Svc = _SERVICE_MAP[role]

    def decorator(func: Callable[..., Awaitable]):
        @wraps(func)
        async def wrapper(event: Event, *args, **kwargs):
            tg_id = event.from_user.id
            session = kwargs.get("session")
            async with Svc(session=session) as svc:
                obj = await svc.get_by_tg(tg_id)

            if not obj:
                try:
                    bot = (
                        event.message.bot
                        if isinstance(event, CallbackQuery)
                        else event.bot
                    )
                    await bot.delete_my_commands(
                        scope=BotCommandScopeChat(chat_id=tg_id)
                    )
                except Exception:
                    pass
                await _send(event, "❌ Вас не знайдено у системі. Почніть з /start.")
                return

            if not obj.is_verified:
                await _send(
                    event,
                    "⏳ Ваш профіль ще проходить верифікацію.\nСпробуйте пізніше або зверніться до адміністратора.",
                    reply_markup=main_menu_kb(role, is_verified=False),
                )
                return

            return await func(event, *args, **kwargs)

        return wrapper

    return decorator

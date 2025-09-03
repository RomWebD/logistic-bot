# bot/decorators/access.py
from functools import wraps
from aiogram.types import Message, CallbackQuery, BotCommandScopeChat
from bot.services.verification import CarrierStatus, get_carrier_status
from typing import Union

from bot.services.client.verification_client import ClientStatus, get_client_status
from bot.ui.keyboards import client_main_kb

from bot.fsm.client_registration import start_registration_flow
from bot.services.client.registration import ClientRegistrationService


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
                    "⏳ Ваш профіль ще проходить верифікацію.\nСпробуйте пізніше або зверніться до адміністратора.",
                    reply_markup=client_main_kb(is_verified=False),
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


def require_registered_client():
    """
    Декоратор гарантує, що користувач існує як Client.
    Якщо ні — запускає flow реєстрації.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(event: Union[Message, CallbackQuery], *args, **kwargs):
            session = kwargs.get("session")  # передаєш із handler через Depends
            service = ClientRegistrationService(session)

            user = (
                event.from_user if isinstance(event, (Message, CallbackQuery)) else None
            )
            if not user:
                return

            client = await service.check_existing(user.id)
            if not client:
                if isinstance(event, CallbackQuery):
                    await event.answer()  # закриваємо лоадінг кружок
                    await start_registration_flow(
                        event.message, state=kwargs.get("state")
                    )
                else:
                    await start_registration_flow(event, state=kwargs.get("state"))
                return

            return await func(event, *args, **kwargs)

        return wrapper

    return decorator


def require_verified_client():
    def decorator(func):
        @wraps(func)
        async def wrapper(
            event: Union[Message, CallbackQuery],
            *args,
            **kwargs,
        ):
            user = event.from_user
            telegram_id = user.id
            client_repo = kwargs.get("client_repo")
            client = await client_repo.get_by_telegram_id(telegram_id)
            # якщо клієнта немає
            if not client:
                # редіректимо на /start
                if isinstance(event, CallbackQuery):
                    await event.message.bot.delete_my_commands(
                        scope=BotCommandScopeChat(chat_id=telegram_id)
                    )
                    await event.message.answer(
                        "❌ Вас не знайдено у системі. Почніть з /start."
                    )
                    await event.answer()
                else:
                    await event.bot.delete_my_commands(
                        scope=BotCommandScopeChat(chat_id=telegram_id)
                    )
                    await event.answer(
                        "❌ Вас не знайдено у системі. Почніть з /start."
                    )
                return

            # якщо в БД лежить str, а в коді Enum — нормалізуємо
            status = await get_client_status(telegram_id)

            if not status:
                try:
                    status = ClientStatus(status)
                except Exception:
                    status = ClientStatus.NOT_VERIFIED

            if status == ClientStatus.VERIFIED:
                # пускаємо в хендлер; ВАЖЛИВО: не передаємо client_repo/session далі,
                # якщо хендлер їх не очікує
                return await func(event, *args, **kwargs)

            if status == ClientStatus.NOT_VERIFIED:
                msg = (
                    "⏳ Ваш профіль ще проходить верифікацію.\n"
                    "Спробуйте пізніше або зверніться до адміністратора."
                )
                if isinstance(event, CallbackQuery):
                    await event.message.answer(
                        msg, reply_markup=client_main_kb(is_verified=False)
                    )
                    await event.answer()
                else:
                    await event.answer(
                        msg, reply_markup=client_main_kb(is_verified=False)
                    )
                return

            # fallback (на випадок інших станів)
            if isinstance(event, CallbackQuery):
                await event.message.answer(
                    "❌ Доступ обмежено. Зверніться до підтримки."
                )
                await event.answer()
            else:
                await event.answer("❌ Доступ обмежено. Зверніться до підтримки.")

        return wrapper

    return decorator

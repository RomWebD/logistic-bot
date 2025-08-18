from aiogram import Dispatcher, Bot
from aiogram.types import BotCommand

import asyncio
import sentry_sdk
from bot.handlers.common import role_selection  # 👈 нове
from bot.handlers.carrier_company import registration as carrier_registration  # 👈 нове
from bot.handlers.carrier_company import menu as carrier_menu  # 👈 нове
from bot.handlers.client import menu as client_menu  # 👈 нове
from bot.handlers.client import registration as client_registration  # 👈 нове
from bot.handlers.client import application  # 👈 нове
from bot.handlers.client import verification  # 👈 нове
from bot.services.bot_commands import remove_menu_for_all
from bot.services.loader import bot
from bot.handlers.carrier_company.car_registration import (
    routers as car_registration_routers,
)

# sentry_sdk.init(
#     dsn=config.SENTRY_DSN,
#     traces_sample_rate=1.0,
# )

dp = Dispatcher()

dp.include_router(role_selection.router)
dp.include_router(carrier_registration.router)
dp.include_router(carrier_menu.router)
dp.include_router(client_registration.router)
dp.include_router(verification.router)
dp.include_router(client_menu.router)
dp.include_router(application.router)
# dp.include_router(carrier_add_car.router)
for r in car_registration_routers:
    dp.include_router(r)


async def set_default_commands(bot: Bot):
    """
    Встановлює базові команди для бота (видимі в меню Telegram)
    """
    commands = [
        BotCommand(command="start", description="🚀 Почати / Перезапустити"),
        # можна ще додати інші глобальні команди
        # BotCommand(command="help", description="ℹ️ Допомога"),
    ]
    await bot.set_my_commands(commands)


async def main():
    await remove_menu_for_all(bot)
    # await bot.delete_my_commands()
    await set_default_commands(bot)  # ⬅️ додаємо сюди

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

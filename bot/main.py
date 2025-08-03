from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, BotCommand
from aiogram.enums import ParseMode
from bot import config
import asyncio
import sentry_sdk
from bot.handlers.common import role_selection  # 👈 нове
from bot.handlers.carrier_company import registration as carrier_registration  # 👈 нове
from bot.handlers.carrier_company import menu as carrier_menu  # 👈 нове
from bot.handlers.client import registration as client_registration  # 👈 нове
from bot.handlers.client import application  # 👈 нове
from bot.services.bot_commands import remove_menu_for_all
from bot.services.loader import bot

# sentry_sdk.init(
#     dsn=config.SENTRY_DSN,
#     traces_sample_rate=1.0,
# )

dp = Dispatcher()

dp.include_router(role_selection.router)
dp.include_router(carrier_registration.router)
dp.include_router(carrier_menu.router)
dp.include_router(client_registration.router)
dp.include_router(application.router)


async def main():
    await remove_menu_for_all(bot) 
    # await bot.delete_my_commands()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

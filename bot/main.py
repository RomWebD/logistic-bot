from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.enums import ParseMode
from bot import config
import asyncio
import sentry_sdk
from aiogram.client.default import DefaultBotProperties
from bot.handlers.common import role_selection  # 👈 нове
from bot.handlers.carrier_company import registration as carrier_registration   # 👈 нове
from bot.handlers.client import registration as client_registration   # 👈 нове
from bot.handlers.client import application    # 👈 нове

# sentry_sdk.init(
#     dsn=config.SENTRY_DSN,
#     traces_sample_rate=1.0,
# )

bot = Bot(
    token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

dp.include_router(role_selection.router)
dp.include_router(carrier_registration.router)
dp.include_router(client_registration.router)
dp.include_router(application.router)


# @dp.message()
# async def echo_handler(message: Message):
#     await message.answer(f"👋 Привіт, {message.from_user.full_name}!")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

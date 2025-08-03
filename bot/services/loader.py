# bot/services/loader.py
from aiogram import Bot
from aiogram.enums import ParseMode
from bot import config
from aiogram.client.default import DefaultBotProperties

bot = Bot(
    token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

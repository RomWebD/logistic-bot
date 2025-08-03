# bot/handlers/user.py

from aiogram import Router, F
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()
role_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🚛 Я перевізник", callback_data="role_carrier")],
        [InlineKeyboardButton(text="📦 Я клієнт", callback_data="role_client")],
    ]
)


@router.message(F.text == "/start")
async def welcome_handler(message: Message):
    
    await message.answer(
        "👋 Вас вітає Logisterium Bot!\n\nБудь ласка, виберіть вашу роль:",
        reply_markup=role_keyboard,
    )

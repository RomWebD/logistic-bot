# bot/ui/main_menu.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from enum import Enum


class Role(str, Enum):
    CLIENT = "client"
    CARRIER = "carrier"


def main_menu_kb(role: Role, *, is_verified: bool) -> InlineKeyboardMarkup:
    check_status_cb = f"{role.value}_check_status"
    profile_cb = f"{role.value}_profile"
    rows = [
        [
            InlineKeyboardButton(
                text="🔄 Перевірити статус", callback_data=check_status_cb
            )
        ],
        [InlineKeyboardButton(text="👤 Мій профіль", callback_data=profile_cb)],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)

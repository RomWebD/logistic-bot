# bot/ui/keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def client_main_kb(is_verified: bool) -> InlineKeyboardMarkup:
    if is_verified:
        # повне меню для верифікованих
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📦 Створити заявку", callback_data="client_application"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="👤 Мій профіль", callback_data="client_profile"
                    )
                ],
            ]
        )
    # обмежене меню для НЕверифікованих
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Перевірити статус", callback_data="client_check_status"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👤 Мій профіль", callback_data="client_profile"
                )
            ],
        ]
    )

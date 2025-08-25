"""
🤖 TELEGRAM СПЕЦИФІЧНІ MIXINS
"""

from sqlalchemy.orm import Mapped, mapped_column, declared_attr
from sqlalchemy import BigInteger, String, Boolean
from typing import Optional


class TelegramUserMixin:
    """
    Основна інформація з Telegram

    Чому окремо:
    - Це специфіка месенджера
    - Не всі моделі прив'язані до Telegram
    - Легко замінити на інший месенджер
    """

    @declared_attr
    def telegram_id(cls) -> Mapped[int]:
        return mapped_column(
            BigInteger,  # BigInteger бо Telegram ID може бути великим
            unique=True,
            nullable=False,
            index=True,
            comment="Telegram User ID",
        )

    @declared_attr
    def telegram_username(cls) -> Mapped[Optional[str]]:
        return mapped_column(
            String(32),  # Max 32 символи в Telegram
            nullable=True,
            index=True,
            comment="Telegram username без @",
        )

    @declared_attr
    def telegram_first_name(cls) -> Mapped[Optional[str]]:
        return mapped_column(
            String(64), nullable=True, comment="Ім'я з Telegram профілю"
        )

    @declared_attr
    def telegram_last_name(cls) -> Mapped[Optional[str]]:
        return mapped_column(
            String(64), nullable=True, comment="Прізвище з Telegram профілю"
        )

    @declared_attr
    def is_bot_blocked(cls) -> Mapped[bool]:
        """Чи заблокував користувач бота"""
        return mapped_column(
            Boolean,
            default=False,
            nullable=False,
            comment="True якщо користувач заблокував бота",
        )

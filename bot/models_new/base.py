# bot/models/base.py
"""
🎯 БАЗОВІ КЛАСИ - це фундамент всієї архітектури
Використовуємо патерн MIXIN - це класи які додають функціональність
"""

from sqlalchemy.orm import Mapped, mapped_column, declared_attr
from sqlalchemy import DateTime, func, Integer, BigInteger, Boolean, String
from datetime import datetime
from bot.database.database import Base
from typing import Optional


class TimestampMixin:
    """
    🔧 MIXIN PATTERN - додає timestamp поля до будь-якої моделі

    Принцип DRY (Don't Repeat Yourself):
    - Замість копіювати created_at/updated_at в кожну модель
    - Ми створюємо mixin і наслідуємо його

    @declared_attr - це декоратор SQLAlchemy для динамічних атрибутів
    """

    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            comment="Час створення запису",
        )

    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),  # Автоматично оновлюється при UPDATE
            comment="Час останнього оновлення",
        )


class VerifiableMixin:
    """
    🔐 MIXIN для верифікації - використовується і для Client і для CarrierCompany

    Принцип SOLID - Single Responsibility:
    - Цей mixin відповідає тільки за верифікацію
    """

    @declared_attr
    def is_verified(cls) -> Mapped[bool]:
        return mapped_column(
            Boolean,
            default=False,
            nullable=False,
            comment="Чи верифікований користувач",
        )

    @declared_attr
    def verified_at(cls) -> Mapped[Optional[datetime]]:
        return mapped_column(
            DateTime(timezone=True), nullable=True, comment="Коли був верифікований"
        )

    @declared_attr
    def verified_by(cls) -> Mapped[Optional[int]]:
        return mapped_column(
            Integer, nullable=True, comment="ID адміна який верифікував"
        )


class TelegramUserMixin:
    """
    🤖 MIXIN для Telegram користувачів

    Інкапсуляція логіки Telegram:
    - Всі Telegram-специфічні поля в одному місці
    """

    @declared_attr
    def telegram_id(cls) -> Mapped[int]:
        return mapped_column(
            BigInteger,
            unique=True,
            index=True,
            nullable=False,
            comment="Telegram ID користувача",
        )

    @declared_attr
    def telegram_username(cls) -> Mapped[Optional[str]]:
        return mapped_column(
            String(255), nullable=True, comment="Telegram username (без @)"
        )


class BaseModel(Base):
    """
    🏗️ АБСТРАКТНИЙ БАЗОВИЙ КЛАС

    __abstract__ = True означає що SQLAlchemy не створить таблицю для цього класу
    Це тільки шаблон для інших моделей

    Переваги:
    1. Всі моделі матимуть id
    2. Можемо додати спільні методи для всіх моделей
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Унікальний ідентифікатор",
    )

    def __repr__(self) -> str:
        """Магічний метод для красивого виводу об'єкта"""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def to_dict(self) -> dict:
        """
        Метод серіалізації - перетворення об'єкта в словник
        Патерн: Data Transfer Object (DTO)
        """
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }

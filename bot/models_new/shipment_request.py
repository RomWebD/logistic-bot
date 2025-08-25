"""
📦 МОДЕЛЬ ЗАЯВКИ НА ПЕРЕВЕЗЕННЯ
"""

from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy import (
    JSON,
    Boolean,
    Float,
    String,
    DateTime,
    Integer,
    Text,
    ForeignKey,
    Enum as SQLEnum,
)
from datetime import datetime
from typing import Optional, List

from bot.models_new.base import BaseModel, TimestampMixin
from bot.models_new import Client, ShipmentOffer
from bot.models_new.enums import ShipmentStatus, CargoType, LoadingType
from bot.services.external.groq import normalize_date_with_groq


class ShipmentRequest(BaseModel, TimestampMixin):
    """
    📋 Заявка на перевезення

    Патерни та принципи:
    1. Entity Pattern - це головна бізнес-сутність
    2. State Pattern - статус змінюється через методи
    3. Validation Pattern - валідація через @validates
    """

    __tablename__ = "shipment_requests"

    # 🔗 ЗВ'ЯЗКИ
    client_telegram_id: Mapped[int] = mapped_column(
        ForeignKey("clients.telegram_id"),
        nullable=False,
        index=True,
        comment="Telegram ID клієнта",
    )

    # 📍 МАРШРУТ - розділяємо для кращого пошуку
    from_city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,  # Індекс для швидкого пошуку
        comment="Місто відправлення",
    )

    to_city: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True, comment="Місто призначення"
    )

    # 📅 ДАТА - зберігаємо і parsed і оригінал
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Дата подачі транспорту",
    )

    date_text: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Оригінальний текст дати від користувача"
    )

    # 📦 ВАНТАЖ
    cargo_type: Mapped[CargoType] = mapped_column(
        SQLEnum(CargoType), nullable=False, comment="Тип вантажу"
    )

    cargo_description: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Детальний опис вантажу"
    )

    # Числові характеристики зберігаємо як числа
    weight_tons: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Вага в тоннах"
    )

    volume_m3: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Об'єм в м³"
    )

    pallet_count: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Кількість палет"
    )

    # 🏗️ ЗАВАНТАЖЕННЯ/РОЗВАНТАЖЕННЯ
    loading_type: Mapped[List[LoadingType]] = mapped_column(
        JSON,  # Зберігаємо як JSON масив
        nullable=False,
        comment="Типи завантаження",
    )

    unloading_type: Mapped[List[LoadingType]] = mapped_column(
        JSON, nullable=False, comment="Типи розвантаження"
    )

    # 💰 ЦІНА
    price: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Ціна в копійках (для точності)"
    )

    price_negotiable: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="Чи можливий торг"
    )

    # 📊 СТАТУС
    status: Mapped[ShipmentStatus] = mapped_column(
        SQLEnum(ShipmentStatus),
        default=ShipmentStatus.DRAFT,
        nullable=False,
        index=True,
        comment="Статус заявки",
    )

    # Додаткові поля
    special_requirements: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Особливі вимоги"
    )

    # 🔗 ВІДНОШЕННЯ
    client: Mapped["Client"] = relationship(
        "Client", back_populates="shipment_requests", foreign_keys=[client_telegram_id]
    )

    offers: Mapped[List["ShipmentOffer"]] = relationship(
        "ShipmentOffer", back_populates="shipment", cascade="all, delete-orphan"
    )

    # 🔒 ВАЛІДАТОРИ - декоратор @validates від SQLAlchemy

    @validates("date_text")
    def validate_and_parse_date(self, key, value):
        """
        Валідатор який автоматично парсить дату через AI
        Патерн: Decorator (декоратор для валідації)
        """
        if not hasattr(self, "_date_parsed"):
            parsed = normalize_date_with_groq(value)
            if not parsed:
                raise ValueError(f"Не можу розпізнати дату: {value}")
            self.date = parsed
            self._date_parsed = True
        return value

    @validates("price")
    def validate_price(self, key, value):
        """Валідація ціни"""
        if isinstance(value, str):
            # Витягуємо числа з рядка
            digits = "".join(filter(str.isdigit, value))
            value = int(digits) if digits else 0

        if value <= 0:
            raise ValueError("Ціна має бути більше нуля")

        # Зберігаємо в копійках для точності
        return value * 100

    @validates("weight_tons")
    def validate_weight(self, key, value):
        """Парсинг ваги з тексту"""
        if isinstance(value, str):
            # "2.5 т" -> 2.5
            import re

            match = re.search(r"(\d+\.?\d*)", value)
            if match:
                value = float(match.group(1))

        if value <= 0:
            raise ValueError("Вага має бути більше нуля")

        return value

    # 🔧 МЕТОДИ БІЗНЕС-ЛОГІКИ

    def can_be_accepted(self) -> bool:
        """
        Чи можна прийняти заявку
        Інкапсуляція бізнес-правил
        """
        return self.status in [ShipmentStatus.PUBLISHED, ShipmentStatus.NEGOTIATING]

    def accept_offer(self, offer_id: int) -> bool:
        """
        Прийняти пропозицію
        Патерн: State Machine
        """
        if not self.can_be_accepted():
            return False

        # Знаходимо пропозицію
        offer = next((o for o in self.offers if o.id == offer_id), None)
        if not offer:
            return False

        # Змінюємо статус
        self.status = ShipmentStatus.ACCEPTED
        offer.is_accepted = True

        # Відхиляємо інші пропозиції
        for other_offer in self.offers:
            if other_offer.id != offer_id:
                other_offer.is_rejected = True

        return True

    def cancel(self, reason: Optional[str] = None) -> bool:
        """Скасування заявки"""
        if self.status in [ShipmentStatus.DELIVERED, ShipmentStatus.CANCELLED]:
            return False

        self.status = ShipmentStatus.CANCELLED
        self.cancellation_reason = reason
        return True

    @property
    def route(self) -> str:
        """
        Property - обчислюване поле
        Getter який виглядає як атрибут
        """
        return f"{self.from_city} → {self.to_city}"

    @property
    def price_uah(self) -> float:
        """Ціна в гривнях (конвертація з копійок)"""
        return self.price / 100

    @property
    def is_expired(self) -> bool:
        """Чи прострочена заявка"""
        return self.date < datetime.now()

    def to_message(self) -> str:
        """
        Форматування для Telegram повідомлення
        Патерн: Template Method
        """
        return f"""📦 <b>Заявка №{self.id}</b>
        
📍 Маршрут: {self.route}
📅 Дата: {self.date.strftime("%d.%m.%Y о %H:%M")}
📦 Вантаж: {self.cargo_description}
⚖️ Вага: {self.weight_tons} т
💰 Ціна: {self.price_uah:,.0f} грн

Статус: {self.status.value}"""

"""
📦 МОДЕЛЬ КЛІЄНТА з використанням mixins
"""

from sqlalchemy.orm import Mapped, relationship
from sqlalchemy import String
from typing import List, Optional

from bot.models_new.base import (
    BaseModel,
    TimestampMixin,
    VerifiableMixin,
    TelegramUserMixin,
)
from bot.models_new.mixins import ContactInfoMixin, CompanyInfoMixin
from bot.models_new import ShipmentRequest, SheetBinding


class Client(
    BaseModel,  # Наслідуємо id та базові методи
    TimestampMixin,  # Додаємо created_at, updated_at
    VerifiableMixin,  # Додаємо is_verified
    TelegramUserMixin,  # Додаємо telegram_id
    ContactInfoMixin,  # Додаємо full_name, phone, email
    CompanyInfoMixin,  # Додаємо company_name, tax_id тощо
):
    """
    🎯 КОМПОЗИЦІЯ через Multiple Inheritance (множинне наслідування)

    Принципи ООП тут:
    1. Наслідування - отримуємо функціональність від 6 класів
    2. Композиція - складаємо клас з готових блоків
    3. DRY - не дублюємо код

    Патерн: Entity (сутність) з Domain-Driven Design
    """

    __tablename__ = "clients"

    # Додаткові поля специфічні тільки для клієнта
    # (якщо потрібні)

    # 🔗 ВІДНОШЕННЯ (Relationships)
    shipment_requests: Mapped[List["ShipmentRequest"]] = relationship(
        "ShipmentRequest",
        back_populates="client",
        cascade="all, delete-orphan",  # Видаляємо заявки при видаленні клієнта
        lazy="dynamic",  # Lazy loading - завантажуємо тільки коли потрібно
    )

    sheet_bindings: Mapped[List["SheetBinding"]] = relationship(
        "SheetBinding",
        primaryjoin="and_(Client.id==SheetBinding.owner_id, SheetBinding.owner_type=='client')",
        foreign_keys="[SheetBinding.owner_id]",
        viewonly=True,  # Read-only відношення
    )

    # 🔧 МЕТОДИ КЛАСУ (бізнес-логіка)

    def can_create_shipment(self) -> bool:
        """
        Метод перевірки чи може клієнт створювати заявки
        Інкапсуляція бізнес-правил
        """
        return self.is_verified

    @property
    def display_name(self) -> str:
        """
        Property - це спосіб створити обчислюване поле
        Виглядає як атрибут, але насправді це метод
        """
        if self.company_name:
            return f"{self.company_name} ({self.full_name})"
        return self.full_name

    def __str__(self) -> str:
        """Магічний метод для строкового представлення"""
        return self.display_name

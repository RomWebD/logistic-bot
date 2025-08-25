"""
📞 КОНТАКТНІ MIXINS - винесено окремо для reusability
"""

from sqlalchemy.orm import Mapped, mapped_column, declared_attr
from sqlalchemy import String
from typing import Optional


class ContactInfoMixin:
    """
    👤 Базова контактна інформація
    Використовується і для Client і для CarrierCompany
    """
    
    @declared_attr
    def full_name(cls) -> Mapped[str]:
        """Патерн: Property через declared_attr"""
        return mapped_column(
            String(255),
            nullable=False,
            comment="ПІБ"
        )
    
    @declared_attr
    def phone(cls) -> Mapped[str]:
        return mapped_column(
            String(20),
            nullable=False,
            index=True,  # Індекс для швидкого пошуку
            comment="Телефон"
        )
    
    @declared_attr
    def email(cls) -> Mapped[Optional[str]]:
        return mapped_column(
            String(255),
            nullable=True,
            unique=True,  # Email має бути унікальним
            index=True,
            comment="Email"
        )


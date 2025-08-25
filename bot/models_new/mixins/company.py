"""
📞 Компанія MIXINS - винесено окремо для reusability
"""

from sqlalchemy.orm import Mapped, mapped_column, declared_attr
from sqlalchemy import String
from typing import Optional


class CompanyInfoMixin:
    """
    🏢 Інформація про компанію
    """

    @declared_attr
    def company_name(cls) -> Mapped[str]:
        return mapped_column(
            String(255), nullable=False, comment="Назва компанії або ФОП"
        )

    @declared_attr
    def tax_id(cls) -> Mapped[str]:
        return mapped_column(
            String(20),
            nullable=False,
            unique=True,
            comment="ЄДРПОУ (8 цифр) або ІПН (10 цифр)",
        )

    @declared_attr
    def address(cls) -> Mapped[Optional[str]]:
        return mapped_column(String(255), nullable=True, comment="Адреса")

    @declared_attr
    def website(cls) -> Mapped[Optional[str]]:
        return mapped_column(String(255), nullable=True, comment="Веб-сайт")

"""
🚛 МОДЕЛЬ КОМПАНІЇ ПЕРЕВІЗНИКА
"""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from typing import List, Optional

from bot.models_new.base import (
    BaseModel,
    TimestampMixin,
    VerifiableMixin,
    TelegramUserMixin,
)
from bot.models_new.mixins import ContactInfoMixin, CompanyInfoMixin
from bot.models_new import TransportVehicle, SheetBinding


class CarrierCompany(
    BaseModel,
    TimestampMixin,
    VerifiableMixin,
    TelegramUserMixin,
    ContactInfoMixin,
    CompanyInfoMixin,
):
    """
    🏢 Компанія перевізника

    Патерн: Aggregate Root (корінь агрегату)
    - CarrierCompany це головна сутність
    - TransportVehicle залежить від неї
    """

    __tablename__ = "carrier_companies"

    # Специфічні поля для перевізника
    google_sheet_url: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True, comment="URL до Google Sheets з автопарком"
    )

    google_sheet_id: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, comment="ID Google Sheets"
    )

    # 🚚 ONE-TO-MANY відношення
    vehicles: Mapped[List["TransportVehicle"]] = relationship(
        "TransportVehicle",
        back_populates="carrier_company",
        cascade="all, delete-orphan",
        lazy="select",  # Завантажуємо одразу з компанією
    )

    sheet_bindings: Mapped[List["SheetBinding"]] = relationship(
        "SheetBinding",
        primaryjoin="and_(CarrierCompany.id==SheetBinding.owner_id, SheetBinding.owner_type=='carrier')",
        foreign_keys="[SheetBinding.owner_id]",
        viewonly=True,
    )

    # 📊 ОБЧИСЛЮВАНІ ВЛАСТИВОСТІ

    @property
    def total_vehicles(self) -> int:
        """Кількість транспорту"""
        return len(self.vehicles) if self.vehicles else 0

    @property
    def total_capacity(self) -> float:
        """Загальна вантажопідйомність"""
        if not self.vehicles:
            return 0.0

        total = 0.0
        for vehicle in self.vehicles:
            try:
                # Витягуємо число з рядка типу "23 т"
                capacity = float(
                    "".join(filter(str.isdigit, vehicle.load_capacity_tons or "0"))
                )
                total += capacity
            except ValueError:
                continue
        return total

    def has_vehicle_type(self, vehicle_type: str) -> bool:
        """Перевірка чи є певний тип транспорту"""
        return any(v.vehicle_type == vehicle_type for v in self.vehicles)

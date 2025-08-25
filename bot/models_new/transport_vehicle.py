"""
🚚 МОДЕЛЬ ТРАНСПОРТНОГО ЗАСОБУ
"""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, String, ForeignKey, Text, Float
from typing import Optional

from bot.models_new.base import BaseModel
from bot.models_new import CarrierCompany
from bot.models_new.enums import VehicleType, LoadingType
from bot.models_new.mixins.base import TimestampMixin


class TransportVehicle(BaseModel, TimestampMixin):
    """
    🚛 Транспортний засіб

    Патерн: Value Object
    - Не має сенсу без CarrierCompany
    - Описує характеристики транспорту
    """

    __tablename__ = "transport_vehicles"

    # 🔗 FOREIGN KEY - зв'язок з компанією
    carrier_company_id: Mapped[int] = mapped_column(
        ForeignKey("carrier_companies.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID компанії власника",
    )

    # Основні характеристики
    vehicle_type: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Тип ТЗ (фура, самоскид, рефрижератор)"
    )

    registration_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False, comment="Державний номер"
    )

    # Вантажні характеристики - зберігаємо як числа для зручності
    load_capacity_tons: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Вантажопідйомність в тоннах"
    )

    body_volume_m3: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Об'єм кузова в м³"
    )

    # Додаткове обладнання як JSON або текст
    loading_equipment: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Обладнання для завантаження (гідроборт, кран тощо)",
    )

    # Водій
    driver_fullname: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    driver_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Статус
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="Чи доступний для рейсів"
    )

    # 🔗 ВІДНОШЕННЯ
    carrier_company: Mapped["CarrierCompany"] = relationship(
        "CarrierCompany", back_populates="vehicles"
    )

    # 🔧 МЕТОДИ

    @property
    def display_name(self) -> str:
        """Красиве відображення"""
        return f"{self.vehicle_type} {self.registration_number}"

    def can_handle_cargo(self, weight: float, volume: Optional[float] = None) -> bool:
        """
        Перевірка чи підходить для вантажу
        Інкапсуляція логіки перевірки
        """
        if weight > self.load_capacity_tons:
            return False

        if volume and self.body_volume_m3:
            return volume <= self.body_volume_m3

        return True

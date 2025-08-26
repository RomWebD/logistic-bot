"""
💼 МОДЕЛЬ ПРОПОЗИЦІЇ ПЕРЕВІЗНИКА
"""

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Text, ForeignKey, Boolean
from typing import Optional

from bot.models.base import BaseModel, TimestampMixin
from bot.models.carrier_company import CarrierCompany
from bot.models.shipment_request import ShipmentRequest
from bot.models.transport_vehicle import TransportVehicle


class ShipmentOffer(BaseModel, TimestampMixin):
    """
    💰 Пропозиція від перевізника на заявку

    Патерн: Value Object
    - Залежить від ShipmentRequest
    - Описує умови перевезення
    """

    __tablename__ = "shipment_offers"

    # 🔗 ЗВ'ЯЗКИ
    shipment_id: Mapped[int] = mapped_column(
        ForeignKey("shipment_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    carrier_company_id: Mapped[int] = mapped_column(
        ForeignKey("carrier_companies.id"), nullable=False, index=True
    )

    vehicle_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("transport_vehicles.id"), nullable=True
    )

    # 💰 ПРОПОЗИЦІЯ
    offered_price: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Запропонована ціна в копійках"
    )

    comment: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Коментар до пропозиції"
    )

    # 📊 СТАТУС
    is_accepted: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Чи прийнята пропозиція"
    )

    is_rejected: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="Чи відхилена пропозиція"
    )

    # 🔗 ВІДНОШЕННЯ
    shipment: Mapped["ShipmentRequest"] = relationship(
        "ShipmentRequest", back_populates="offers"
    )

    carrier_company: Mapped["CarrierCompany"] = relationship("CarrierCompany")

    vehicle: Mapped[Optional["TransportVehicle"]] = relationship("TransportVehicle")

    # 🔧 МЕТОДИ

    @property
    def price_uah(self) -> float:
        """Ціна в гривнях"""
        return self.offered_price / 100

    @property
    def is_pending(self) -> bool:
        """Чи очікує на рішення"""
        return not self.is_accepted and not self.is_rejected

    def accept(self) -> None:
        """
        Прийняти пропозицію
        Метод змінює внутрішній стан - Encapsulation
        """
        self.is_accepted = True
        self.is_rejected = False

    def reject(self) -> None:
        """Відхилити пропозицію"""

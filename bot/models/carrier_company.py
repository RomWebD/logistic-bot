from sqlalchemy import String, Boolean, BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from bot.database.database import Base
from typing import List, Optional
from datetime import datetime



class CarrierCompany(Base):
    __tablename__ = "carrier_companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, comment="Telegram ID користувача"
    )

    # Верифікація
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Контактна інформація
    full_name: Mapped[str] = mapped_column(String(255), comment="ПІБ контактної особи")
    phone: Mapped[str] = mapped_column(String(32), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    # Компанія
    company_name: Mapped[str] = mapped_column(String(255))
    tax_id: Mapped[str] = mapped_column(String(20), unique=True)
    address: Mapped[str] = mapped_column(String(255))
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    # Відношення
    vehicles: Mapped[List["TransportVehicle"]] = relationship(
        back_populates="carrier_company",
        cascade="all, delete-orphan",
    )

    @property
    def display_name(self) -> str:
        """Ім'я для відображення"""
        return f"{self.company_name} ({self.full_name})"

    @property
    def total_vehicles(self) -> int:
        """Кількість транспорту"""
        return len(self.vehicles) if self.vehicles else 0

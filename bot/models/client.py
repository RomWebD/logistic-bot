from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, BigInteger, Boolean, DateTime, func
from datetime import datetime
from bot.database.database import Base
from typing import Optional, List
from bot.models.shipment_request import ShipmentRequest


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)

    # Верифікація - просто is_verified, без зайвого
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Контактні дані
    full_name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True)

    # Компанія
    company_name: Mapped[Optional[str]] = mapped_column(String(150))
    tax_id: Mapped[Optional[str]] = mapped_column(String(20))
    address: Mapped[Optional[str]] = mapped_column(String(255))
    website: Mapped[Optional[str]] = mapped_column(String(255))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Відношення
    shipment_requests: Mapped[List["ShipmentRequest"]] = relationship(
        "ShipmentRequest", back_populates="client"
    )

    @property
    def display_name(self) -> str:
        """Ім'я для відображення"""
        if self.company_name:
            return f"{self.company_name} ({self.full_name})"
        return self.full_name

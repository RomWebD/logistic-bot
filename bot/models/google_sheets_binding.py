from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    String,
    BigInteger,
    DateTime,
    Boolean,
    Enum,
    UniqueConstraint,
    func,
)
from datetime import datetime
from bot.database.database import Base
from typing import Optional
import enum


class OwnerType(enum.Enum):
    CLIENT = "client"
    CARRIER = "carrier"
    DRIVER = "driver"


class SheetType(enum.Enum):
    REQUESTS = "Заявки"  # Заявки
    VEHICLES = "Автопарк"  # Автопарк
    TRIPS = "Рейси"  # Рейси


class GoogleSheetBinding(Base):
    """
    Універсальна таблиця для зв'язку з Google Sheets
    Один власник може мати кілька таблиць різних типів
    """

    __tablename__ = "google_sheet_bindings"
    __table_args__ = (
        UniqueConstraint(
            "telegram_id",
            "owner_type",
            "sheet_type",
            name="uq_binding_owner_sheet_type",
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)

    # Власник
    telegram_id: Mapped[int] = mapped_column(BigInteger, index=True)
    owner_type: Mapped[OwnerType] = mapped_column(Enum(OwnerType))
    sheet_type: Mapped[SheetType] = mapped_column(Enum(SheetType))

    # Google Sheets
    sheet_id: Mapped[str] = mapped_column(String(128), unique=True)
    sheet_url: Mapped[str] = mapped_column(String(512))

    # Ревізії для синхронізації
    last_revision_id: Mapped[Optional[str]] = mapped_column(String(64))
    last_modified_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    last_modified_by_email: Mapped[Optional[str]] = mapped_column(String(255))

    # Синхронізація
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_synced_revision: Mapped[Optional[str]] = mapped_column(String(64))
    sync_in_progress: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def needs_sync(self) -> bool:
        """Перевірка чи потрібна синхронізація"""
        if not self.last_synced_revision:
            return True
        return self.last_synced_revision != self.last_revision_id

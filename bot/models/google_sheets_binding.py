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
    REQUESTS = "Заявки"
    VEHICLES = "Автопарк"
    TRIPS = "Рейси"


class SheetStatus(enum.Enum):
    """Статуси Google Sheet"""

    NONE = "none"  # Не створено
    CREATING = "creating"  # Створюється
    READY = "ready"  # Готовий
    FAILED = "failed"  # Помилка
    SYNCING = "syncing"  # Синхронізується


class GoogleSheetBinding(Base):
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
    sheet_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    sheet_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Статус
    status: Mapped[SheetStatus] = mapped_column(
        Enum(SheetStatus), default=SheetStatus.NONE, nullable=False
    )

    # Ревізії для синхронізації
    last_revision_id: Mapped[Optional[str]] = mapped_column(String(64))
    last_modified_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    last_modified_by_email: Mapped[Optional[str]] = mapped_column(String(255))

    # Синхронізація
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_synced_revision: Mapped[Optional[str]] = mapped_column(String(64))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def needs_sync(self) -> bool:
        """Перевірка чи потрібна синхронізація"""
        if self.status != SheetStatus.READY:
            return False
        if not self.last_synced_revision:
            return True
        return self.last_synced_revision != self.last_revision_id

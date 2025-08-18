# bot/models/sheets.py
from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    String,
    Integer,
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    UniqueConstraint,
    ForeignKey,
)
from bot.database.database import Base
from enum import Enum as PyEnum


class SheetKindEnum(str):
    requests = "requests"
    vehicles = "vehicles"


# SQLAlchemy Enum (з фіксованими значеннями)


class SheetKind(PyEnum):
    requests = "requests"
    vehicles = "vehicles"


class SheetBinding(Base):
    __tablename__ = "sheet_bindings"
    __table_args__ = (
        UniqueConstraint("owner_telegram_id", "kind", name="uq_binding_owner_kind"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("clients.telegram_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    kind: Mapped[SheetKind] = mapped_column(Enum(SheetKind), nullable=False)

    sheet_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    sheet_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # останній перегляд розділу
    last_opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_opened_revision: Mapped[Optional[str]] = mapped_column(String(64))
    last_opened_by_email: Mapped[Optional[str]] = mapped_column(String(255))
    last_opened_by_name: Mapped[Optional[str]] = mapped_column(String(255))
    last_opened_modified_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    # останній синк
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_synced_revision: Mapped[Optional[str]] = mapped_column(String(64))

    # контроль одночасних/частих синків
    sync_in_progress: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    cooldown_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

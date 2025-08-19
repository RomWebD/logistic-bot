# bot/models/sheets.py
from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    Enum,
    UniqueConstraint,
    func,
    text,
)
from bot.database.database import Base
from enum import Enum as PyEnum


class OwnerType(PyEnum):
    client = "client"
    carrier = "carrier"


class SheetKind(PyEnum):
    requests = "requests"
    vehicles = "vehicles"


class SheetBinding(Base):
    __tablename__ = "sheet_bindings"
    __table_args__ = (
        UniqueConstraint(
            "owner_id", "owner_type", "kind", name="uq_binding_owner_kind"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    owner_id: Mapped[int] = mapped_column(nullable=False)
    owner_type: Mapped[OwnerType] = mapped_column(Enum(OwnerType), nullable=False)
    kind: Mapped[SheetKind] = mapped_column(Enum(SheetKind), nullable=False)

    sheet_id: Mapped[str | None] = mapped_column(String(128))
    sheet_url: Mapped[str | None] = mapped_column(String(512))

    # 👇 тільки останній стан
    last_revision_id: Mapped[str | None] = mapped_column(String(64))
    last_modified_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_modified_by_email: Mapped[str | None] = mapped_column(String(255))
    last_modified_by_name: Mapped[str | None] = mapped_column(String(255))

    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_synced_revision: Mapped[str | None] = mapped_column(String(64))

    sync_in_progress: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    cooldown_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

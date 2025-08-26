# bot/models/sheets.py
from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, DateTime, ForeignKey, func
from bot.database.database import Base


class SheetBindingLog(Base):
    __tablename__ = "sheet_binding_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    binding_id: Mapped[int] = mapped_column(
        ForeignKey("sheet_bindings.id", ondelete="CASCADE"), nullable=False, index=True
    )

    revision_id: Mapped[str] = mapped_column(String(64), nullable=False)
    modified_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    modified_by_email: Mapped[str | None] = mapped_column(String(255))
    modified_by_name: Mapped[str | None] = mapped_column(String(255))

    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_sync_event: Mapped[bool] = mapped_column(Boolean, default=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

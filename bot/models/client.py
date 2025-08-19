# bot/database/models.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, BigInteger, Boolean, func, text, DateTime
from bot.database.database import Base
import enum

# bot/models/sheets.py
from datetime import datetime


class SheetStatus(str, enum.Enum):
    PENDING = "pending"
    READY = "ready"
    FAILED = "failed"
    NONE = "none"


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=False
    )

    is_verify: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("FALSE")
    )

    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    company_name: Mapped[str | None] = mapped_column(String(150))
    tax_id: Mapped[str | None] = mapped_column(String(20))

    phone: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, index=True
    )
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    address: Mapped[str | None] = mapped_column(String(255))
    website: Mapped[str | None] = mapped_column(String(255))


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    # google_sheet_url: Mapped[str | None] = mapped_column(
    #     String(512), nullable=True, comment="URL до Google Sheets із автопарком"
    # )
    # google_sheet_id: Mapped[str | None] = mapped_column(
    #     String(512), nullable=True, comment="URL до Google Sheets із заявками"
    # )
    # sheet_status: Mapped[str] = mapped_column(
    #     Enum(SheetStatus), default=SheetStatus.NONE, nullable=False
    # )

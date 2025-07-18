# bot/models/request.py

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer, Text, ForeignKey, func
from datetime import datetime
from bot.ai_helper.date_parser import normalize_date_with_groq
from bot.database.database import Base
from sqlalchemy.orm import validates
import dateparser


class Shipment_request(Base):
    __tablename__ = "shipment_request"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_telegram_id: Mapped[int] = mapped_column(unique=True, index=True)
    from_city: Mapped[str] = mapped_column(String)
    to_city: Mapped[str] = mapped_column(String)

    date: Mapped[datetime] = mapped_column(DateTime)
    date_text: Mapped[str] = mapped_column(String)
    cargo_type: Mapped[str] = mapped_column(String)
    volume: Mapped[str] = mapped_column(String)
    weight: Mapped[str] = mapped_column(String)
    loading: Mapped[str] = mapped_column(String)
    unloading: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    @validates("date")
    def validate_date(self, key, value):
        if isinstance(value, str):
            parsed = normalize_date_with_groq(value)
            if parsed is None:
                raise ValueError("Невалідна дата")
            return parsed
        return value

    @validates("price")
    def validate_price(self, key, value):
        if isinstance(value, str):
            digits = "".join(filter(str.isdigit, value))
            return int(digits or 0)
        return value

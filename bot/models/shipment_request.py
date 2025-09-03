from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy import String, DateTime, Text, ForeignKey, func
from datetime import datetime
from bot.database.database import Base
from bot.services.external.groq import normalize_date_with_groq


class ShipmentRequest(Base):
    """
    Проста модель без оверінжинірингу
    SQLAlchemy валідація тільки для критичних випадків
    """

    __tablename__ = "shipment_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_telegram_id: Mapped[int] = mapped_column(
        ForeignKey("clients.telegram_id"), index=True
    )

    # Маршрут
    from_city: Mapped[str] = mapped_column(String(100), nullable=True)
    to_city: Mapped[str] = mapped_column(String(100), nullable=True)

    # Дата
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    date_text: Mapped[str] = mapped_column(String(255))  # Оригінальний текст

    # Вантаж - зберігаємо як текст, валідація в Pydantic
    cargo_type: Mapped[str] = mapped_column(String(50), nullable=True)
    cargo_description: Mapped[str] = mapped_column(Text, nullable=True)

    # Прості поля без складної валідації
    weight: Mapped[str] = mapped_column(String(20), nullable=True)  # "2.5 т"
    volume: Mapped[str] = mapped_column(String(20), nullable=True)  # "20 м³"
    loading: Mapped[str] = mapped_column(String(100), nullable=True)
    unloading: Mapped[str] = mapped_column(String(100), nullable=True)

    # Ціна в копійках для точності
    price: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Опис та статус
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # Відношення
    client: Mapped["Client"] = relationship(
        "Client", back_populates="shipment_requests"
    )

    @validates("date")
    def validate_date(self, key, value):
        if isinstance(value, str):
            parsed = normalize_date_with_groq(value)
            if parsed is None:
                raise ValueError("Невалідна дата")
            return parsed
        return value

    @property
    def route(self) -> str:
        """Простий property для маршруту"""
        return f"{self.from_city} → {self.to_city}"

    def to_message(self) -> str:
        """
        Форматування для Telegram повідомлення
        Патерн: Template Method
        """
        return f"""📦 <b>Заявка №{self.id}</b>
        
📍 Маршрут: {self.route}
📅 Дата: {self.date.strftime("%d.%m.%Y о %H:%M")}
📦 Вантаж: {self.cargo_description}
⚖️ Вага: {self.weight_tons} т
💰 Ціна: {self.price_uah:,.0f} грн

Статус: {self.status.value}"""

from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Integer, Text, ForeignKey, func
from datetime import datetime
from bot.database.database import Base


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
    from_city: Mapped[str] = mapped_column(String(100))
    to_city: Mapped[str] = mapped_column(String(100))

    # Дата
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    date_text: Mapped[str] = mapped_column(String(255))  # Оригінальний текст

    # Вантаж - зберігаємо як текст, валідація в Pydantic
    cargo_type: Mapped[str] = mapped_column(String(50))
    cargo_description: Mapped[str] = mapped_column(Text)

    # Прості поля без складної валідації
    weight: Mapped[str] = mapped_column(String(20))  # "2.5 т"
    volume: Mapped[str] = mapped_column(String(20), nullable=True)  # "20 м³"
    loading: Mapped[str] = mapped_column(String(100))
    unloading: Mapped[str] = mapped_column(String(100))

    # Ціна в копійках для точності
    price: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Опис та статус
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft")

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Відношення
    client: Mapped["Client"] = relationship(
        "Client", back_populates="shipment_requests"
    )

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

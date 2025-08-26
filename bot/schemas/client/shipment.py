from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
import re


class ShipmentRequestCreateData(BaseModel):
    """DTO для створення заявки - тут вся валідація"""

    client_telegram_id: int
    from_city: str = Field(..., min_length=2, max_length=100)
    to_city: str = Field(..., min_length=2, max_length=100)
    date_text: str  # Оригінальний текст
    date: Optional[datetime] = None  # Буде заповнено через AI
    cargo_type: str
    weight: str
    volume: Optional[str] = None
    loading: str
    unloading: str
    price: int  # В гривнях, конвертуємо в копійки
    description: Optional[str] = None

    @field_validator("price")
    @classmethod
    def convert_price_to_kopiyky(cls, v: int) -> int:
        """Конвертуємо в копійки для збереження"""
        if v <= 0:
            raise ValueError("Ціна має бути більше нуля")
        return v * 100

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v: str) -> str:
        """Базова перевірка ваги"""
        if not v or len(v) < 1:
            raise ValueError("Вага обов'язкова")
        return v

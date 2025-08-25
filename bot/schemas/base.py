"""
Базові схеми для DTO (Data Transfer Objects)
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class BaseSchema(BaseModel):
    """Базова схема з налаштуваннями"""
    model_config = ConfigDict(
        from_attributes=True,  # Дозволяє створювати з SQLAlchemy моделей
        str_strip_whitespace=True,  # Автоматично прибирає пробіли
        validate_assignment=True  # Валідація при присвоєнні
    )


class TimestampSchema(BaseSchema):
    """Схема з timestamp полями"""
    created_at: datetime
    updated_at: datetime
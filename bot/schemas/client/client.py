"""
Схеми для клієнтів - це як TypeScript інтерфейси
"""
from bot.schemas.base import BaseSchema, TimestampSchema
from typing import Optional
from pydantic import field_validator, EmailStr
import re


class ClientRegistrationData(BaseSchema):
    """DTO для реєстрації клієнта"""
    telegram_id: int
    full_name: str
    phone: str
    email: EmailStr
    company_name: str
    tax_id: str
    address: str
    website: Optional[str] = None
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Валідація телефону з Pydantic"""
        cleaned = ''.join(filter(str.isdigit, v))
        if len(cleaned) not in [10, 12]:
            raise ValueError('Невірний формат телефону')
        return cleaned
    
    @field_validator('tax_id')
    @classmethod
    def validate_tax_id(cls, v: str) -> str:
        """Валідація ЄДРПОУ/ІПН"""
        if not v.isdigit() or len(v) not in [8, 10]:
            raise ValueError('ЄДРПОУ має бути 8 цифр, ІПН - 10 цифр')
        return v


class ClientResponse(TimestampSchema):
    """Схема для відповіді з даними клієнта"""
    id: int
    telegram_id: int
    full_name: str
    phone: str
    email: str
    company_name: str
    is_verified: bool = False
    rating: Optional[float] = None
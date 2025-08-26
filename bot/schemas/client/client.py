"""
Схеми для клієнтів - це як TypeScript інтерфейси
"""

from bot.schemas.base import BaseSchema, TimestampSchema
from typing import Optional
from pydantic import field_validator, EmailStr
import re
from pydantic import BaseModel, Field
from bot.schemas.validators import PhoneValidatorMixin


"""
Використання в схемах
"""


class ClientRegistrationData(BaseModel, PhoneValidatorMixin):
    """DTO для реєстрації клієнта з валідацією телефону"""

    telegram_id: int
    full_name: str
    phone: str  # Буде автоматично валідуватись і форматуватись
    email: str
    company_name: str
    tax_id: str
    address: str
    country_code: str = Field(default="UA", exclude=True)  # Для валідації телефону


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

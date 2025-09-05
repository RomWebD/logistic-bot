from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
import re


class CarrierRegistrationData(BaseModel):
    """DTO для реєстрації перевізника"""

    telegram_id: int
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: str = Field(..., min_length=10, max_length=32)
    email: EmailStr
    company_name: str = Field(..., min_length=2, max_length=255)
    tax_id: str = Field(..., pattern=r"^\d{8}$|^\d{10}$")
    address: str = Field(..., min_length=5, max_length=255)
    website: Optional[str] = Field(None, max_length=255)

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        """Нормалізація телефону"""
        digits = re.sub(r"\D", "", v)
        if len(digits) == 10 and digits.startswith("0"):
            return f"+380{digits[1:]}"
        elif len(digits) == 12 and digits.startswith("380"):
            return f"+{digits}"
        return v

    @field_validator("website")
    @classmethod
    def validate_website(cls, v: Optional[str]) -> Optional[str]:
        """Валідація URL"""
        if not v or v == "-":
            return None
        if not v.startswith(("http://", "https://")):
            v = f"https://{v}"
        return v


class CarrierUpdateData(BaseModel):
    """DTO для оновлення даних перевізника"""

    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, min_length=10, max_length=32)
    email: Optional[EmailStr] = None
    company_name: Optional[str] = Field(None, min_length=2, max_length=255)
    address: Optional[str] = Field(None, min_length=5, max_length=255)
    website: Optional[str] = Field(None, max_length=255)


class CarrierResponse(BaseModel):
    """DTO для відповіді"""

    id: int
    telegram_id: int
    full_name: str
    phone: str
    email: str
    company_name: str
    tax_id: str
    is_verified: bool
    total_vehicles: int = 0

    class Config:
        from_attributes = True

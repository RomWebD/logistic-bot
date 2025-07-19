# bot/schemas/carrier_company.py

from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional


class CarrierCompanyBase(BaseModel):
    contact_full_name: str = Field(..., max_length=255, description="ПІБ контактної особи")
    phone: str = Field(..., max_length=20, description="Мобільний телефон")
    email: EmailStr = Field(..., description="Електронна пошта")

    company_name: str = Field(..., max_length=255, description="Назва компанії або ФОП")
    ownership_type: str = Field(..., max_length=100, description="Форма власності (ТОВ, ФОП тощо)")
    tax_id: str = Field(..., max_length=20, description="ЄДРПОУ / ІПН")
    office_address: str = Field(..., max_length=255, description="Адреса офісу")
    website: Optional[HttpUrl] = Field(None, description="Вебсайт компанії")


class CarrierCompanyCreate(CarrierCompanyBase):
    """Схема для створення компанії"""
    pass


class CarrierCompanyOut(CarrierCompanyBase):
    """Схема для відповіді API"""
    id: int

    class Config:
        orm_mode = True

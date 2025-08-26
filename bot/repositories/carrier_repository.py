from bot.repositories.base import BaseRepository
from bot.models.carrier_company import CarrierCompany
from typing import Optional, List
from sqlalchemy import select


class CarrierRepository(BaseRepository[CarrierCompany]):
    
    def __init__(self, session):
        super().__init__(session, CarrierCompany)
    
    async def find_by_email(self, email: str) -> Optional[CarrierCompany]:
        """Пошук за email"""
        result = await self.session.execute(
            select(CarrierCompany).where(CarrierCompany.email == email)
        )
        return result.scalar_one_or_none()
    
    async def find_by_tax_id(self, tax_id: str) -> Optional[CarrierCompany]:
        """Пошук за ЄДРПОУ/ІПН"""
        result = await self.session.execute(
            select(CarrierCompany).where(CarrierCompany.tax_id == tax_id)
        )
        return result.scalar_one_or_none()
    
    async def get_verified_carriers(self) -> List[CarrierCompany]:
        """Отримати верифікованих перевізників"""
        result = await self.session.execute(
            select(CarrierCompany).where(CarrierCompany.is_verified == True)
        )
        return list(result.scalars().all())
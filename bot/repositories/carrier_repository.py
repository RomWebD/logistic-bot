# bot/repositories/carrier_company_repository.py
from typing import Optional
from sqlalchemy import select
from bot.repositories.base import BaseRepository
from bot.models.carrier_company import CarrierCompany
from sqlalchemy import func
from bot.models.transport_vehicle import TransportVehicle


class CarrierCompanyRepository(BaseRepository[CarrierCompany]):
    def __init__(self, session):
        super().__init__(session, CarrierCompany)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[CarrierCompany]:
        res = await self.session.execute(
            select(CarrierCompany).where(CarrierCompany.telegram_id == telegram_id)
        )
        return res.scalar_one_or_none()

    async def find_by_phone(self, phone: str) -> Optional[CarrierCompany]:
        res = await self.session.execute(
            select(CarrierCompany).where(CarrierCompany.phone == phone)
        )
        return res.scalar_one_or_none()

    async def find_by_email(self, email: str) -> Optional[CarrierCompany]:
        if not email:
            return None
        res = await self.session.execute(
            select(CarrierCompany).where(CarrierCompany.email == email)
        )
        return res.scalar_one_or_none()

    async def count_vehicles(self, carrier_id: int) -> int:
        q = select(func.count(TransportVehicle.id)).where(
            TransportVehicle.carrier_company_id == carrier_id
        )
        return int(await self.session.scalar(q) or 0)

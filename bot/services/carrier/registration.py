# bot/services/carrier/registration.py
from typing import Optional, Dict, Any
from sqlalchemy.exc import IntegrityError
from bot.services.base_service import BaseService
from bot.repositories.carrier_repository import CarrierCompanyRepository
from bot.schemas.carrier.carrier import CarrierRegistrationData, CarrierResponse
from bot.models.carrier_company import CarrierCompany


class CarrierRegistrationService(BaseService[CarrierCompany]):
    def __init__(self, session: Optional["AsyncSession"] = None):
        super().__init__(session)

    @property
    def repo(self) -> CarrierCompanyRepository:
        return CarrierCompanyRepository(self.session)

    async def get_by_tg(self, telegram_id: int) -> Optional[CarrierCompany]:
        return await self.repo.get_by_telegram_id(telegram_id)

    async def check_existing(self, telegram_id: int) -> Optional[CarrierCompany]:
        return await self.repo.get_by_telegram_id(telegram_id)

    async def is_verified(self, telegram_id: int) -> bool:
        c = await self.get_by_tg(telegram_id)
        return bool(c and c.is_verified)

    async def register(self, data: CarrierRegistrationData) -> Dict[str, Any]:
        try:
            existing = await self.get_by_tg(data.telegram_id)
            if existing:
                resp = CarrierResponse.model_validate(existing)
                resp.total_vehicles = await self.repo.count_vehicles(existing.id)
                return {
                    "success": False,
                    "code": "CARRIER_EXISTS",
                    "message": "Ви вже зареєстровані як перевізник",
                    "carrier": resp.model_dump(),
                }

            carrier = await self.repo.create(**data.model_dump())
            await self.session.commit()

            resp = CarrierResponse.model_validate(carrier)
            resp.total_vehicles = 0  # щойно створений — 0
            return {
                "success": True,
                "message": "Реєстрація успішна",
                "carrier": resp.model_dump(),
            }

        except IntegrityError:
            await self.session.rollback()
            existing = await self.get_by_tg(data.telegram_id)
            resp = CarrierResponse.model_validate(existing) if existing else None
            if resp:
                resp.total_vehicles = await self.repo.count_vehicles(existing.id)
            return {
                "success": False,
                "code": "CARRIER_EXISTS",
                "message": "Ви вже зареєстровані як перевізник",
                "carrier": resp.model_dump() if resp else None,
            }

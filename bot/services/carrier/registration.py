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

    async def register(self, data: CarrierRegistrationData) -> Dict[str, Any]:
        try:
            existing = await self.get_by_tg(data.telegram_id)
            if existing:
                return {
                    "success": False,
                    "code": "CARRIER_EXISTS",
                    "message": "Ви вже зареєстровані як перевізник",
                    "carrier": CarrierResponse.model_validate(existing).model_dump(),
                }

            carrier = await self.repo.create(**data.model_dump())
            await self.session.commit()

            return {
                "success": True,
                "message": "Реєстрація успішна",
                "carrier": CarrierResponse.model_validate(carrier).model_dump(),
            }

        except IntegrityError:
            await self.session.rollback()
            existing = await self.get_by_tg(data.telegram_id)
            return {
                "success": False,
                "code": "CARRIER_EXISTS",
                "message": "Ви вже зареєстровані як перевізник",
                "carrier": CarrierResponse.model_validate(existing).model_dump() if existing else None,
            }
        except Exception as e:
            await self.session.rollback()
            await self.handle_error(e, "register_carrier")
            return {"success": False, "code": "REGISTRATION_ERROR", "message": "Помилка реєстрації"}

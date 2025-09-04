from bot.repositories.carrier_repository import CarrierCompanyRepository
from bot.repositories.google_sheet_repository import GoogleSheetRepository
from bot.models.google_sheets_binding import OwnerType, SheetType
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession


class CarrierService:
    """
    Сервіс для роботи з перевізниками
    Інкапсулює всю бізнес-логіку
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.carrier_repo = CarrierCompanyRepository(session)
        self.sheet_repo = GoogleSheetRepository(session)

    async def get_vehicles_sheet_url(self, telegram_id: int) -> Optional[str]:
        """
        Отримати URL таблиці з транспортом
        Бізнес-логіка: перевіряємо чи є перевізник і чи верифікований
        """
        # 1. Перевіряємо чи існує перевізник
        carrier = await self.carrier_repo.get_by_telegram_id(telegram_id)
        if not carrier:
            return None

        # 2. Перевіряємо верифікацію (бізнес-правило)
        if not carrier.is_verified:
            return None

        # 3. Шукаємо Google Sheet binding
        binding = await self.sheet_repo.get_by_owner_and_type(
            telegram_id=telegram_id,
            owner_type=OwnerType.CARRIER,
            sheet_type=SheetType.VEHICLES,
        )

        return binding.sheet_url if binding else None

    async def get_carrier_info(self, telegram_id: int) -> Dict[str, Any]:
        """
        Отримати повну інформацію про перевізника
        Композиція даних з різних джерел
        """
        carrier = await self.carrier_repo.get_by_telegram_id(telegram_id)

        if not carrier:
            return {"exists": False}

        # Отримуємо всі sheets
        sheets = await self.sheet_repo.get_by_telegram_id(telegram_id)

        return {
            "exists": True,
            "carrier": carrier,
            "is_verified": carrier.is_verified,
            "total_vehicles": carrier.total_vehicles,
            "sheets": {
                SheetType.VEHICLES: next(
                    (s for s in sheets if s.sheet_type == SheetType.VEHICLES), None
                ),
                SheetType.TRIPS: next(
                    (s for s in sheets if s.sheet_type == SheetType.TRIPS), None
                ),
            },
        }

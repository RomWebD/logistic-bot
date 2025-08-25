
# bot/repositories/carrier_repository.py
from bot.repositories.base import BaseRepository
from bot.models.carrier import Carrier
from typing import List
from sqlalchemy import select


class CarrierRepository(BaseRepository[Carrier]):
    """Репозиторій для перевізників"""
    
    def __init__(self, session):
        super().__init__(Carrier, session)
    
    async def find_by_route(self, route: str) -> List[Carrier]:
        """Знайти всіх перевізників за маршрутом"""
        result = await self.session.execute(
            select(Carrier).where(Carrier.route.contains(route))
        )
        return list(result.scalars().all())
    
    async def get_active_carriers(self) -> List[Carrier]:
        """Отримати активних перевізників (можна додати поле is_active)"""
        # Поки що повертаємо всіх
        return await self.get_all()
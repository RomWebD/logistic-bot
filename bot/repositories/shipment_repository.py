from bot.repositories.base import BaseRepository
from bot.models.shipment_request import ShipmentRequest
from typing import List, Optional
from sqlalchemy import select, func
from datetime import datetime


class ShipmentRepository(BaseRepository[ShipmentRequest]):
    
    def __init__(self, session):
        super().__init__(session, ShipmentRequest)
    
    async def get_active_requests(self) -> List[ShipmentRequest]:
        """Отримати активні заявки"""
        result = await self.session.execute(
            select(ShipmentRequest).where(
                ShipmentRequest.date > datetime.now()
            )
        )
        return list(result.scalars().all())
    
    async def get_by_client(self, client_telegram_id: int) -> List[ShipmentRequest]:
        """Отримати заявки клієнта"""
        result = await self.session.execute(
            select(ShipmentRequest).where(
                ShipmentRequest.client_telegram_id == client_telegram_id
            )
        )
        return list(result.scalars().all())
    
    async def get_by_route(self, from_city: str, to_city: str) -> List[ShipmentRequest]:
        """Знайти заявки за маршрутом"""
        result = await self.session.execute(
            select(ShipmentRequest).where(
                ShipmentRequest.from_city == from_city,
                ShipmentRequest.to_city == to_city
            )
        )
        return list(result.scalars().all())
    
    async def count_by_client(self, client_telegram_id: int) -> int:
        """Порахувати кількість заявок клієнта"""
        result = await self.session.execute(
            select(func.count(ShipmentRequest.id)).where(
                ShipmentRequest.client_telegram_id == client_telegram_id
            )
        )
        return result.scalar() or 0
    
    async def create_batch(self, requests_data: List[dict]) -> List[ShipmentRequest]:
        """Створити кілька заявок одночасно"""
        requests = [ShipmentRequest(**data) for data in requests_data]
        self.session.add_all(requests)
        await self.session.commit()
        return requests
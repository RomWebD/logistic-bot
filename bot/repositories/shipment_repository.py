# bot/repositories/shipment_repository.py
from bot.repositories.base import BaseRepository
from bot.models.shipment_request import Shipment_request
from typing import List, Optional
from sqlalchemy import select
from datetime import datetime


class ShipmentRepository(BaseRepository[Shipment_request]):
    """Репозиторій для заявок на перевезення"""
    
    def __init__(self, session):
        super().__init__(Shipment_request, session)
    
    async def get_active_requests(self) -> List[Shipment_request]:
        """Отримати активні заявки (де дата в майбутньому)"""
        result = await self.session.execute(
            select(Shipment_request).where(
                Shipment_request.date > datetime.now()
            )
        )
        return list(result.scalars().all())
    
    async def get_by_client(self, client_telegram_id: int) -> List[Shipment_request]:
        """Отримати всі заявки клієнта"""
        result = await self.session.execute(
            select(Shipment_request).where(
                Shipment_request.client_telegram_id == client_telegram_id
            )
        )
        return list(result.scalars().all())
    
    async def get_by_route(self, route: str) -> List[Shipment_request]:
        """Знайти заявки за маршрутом"""
        result = await self.session.execute(
            select(Shipment_request).where(
                Shipment_request.route.contains(route)
            )
        )
        return list(result.scalars().all())
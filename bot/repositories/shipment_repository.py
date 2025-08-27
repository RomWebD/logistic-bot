from bot.models.client import Client
from bot.repositories.base import BaseRepository
from bot.models.shipment_request import ShipmentRequest
from typing import List, Optional, Tuple
from sqlalchemy import select, func
from datetime import datetime


class ShipmentRepository(BaseRepository[ShipmentRequest]):
    def __init__(self, session):
        super().__init__(session, ShipmentRequest)

    async def get_active_requests(self) -> List[ShipmentRequest]:
        result = await self.session.execute(
            select(ShipmentRequest).where(ShipmentRequest.date > datetime.now())
        )
        return list(result.scalars().all())

    async def get_by_client(self, client_telegram_id: int) -> List[ShipmentRequest]:
        result = await self.session.execute(
            select(ShipmentRequest).where(
                ShipmentRequest.client_telegram_id == client_telegram_id
            )
        )
        return list(result.scalars().all())

    async def get_by_route(self, from_city: str, to_city: str) -> List[ShipmentRequest]:
        result = await self.session.execute(
            select(ShipmentRequest).where(
                ShipmentRequest.from_city == from_city,
                ShipmentRequest.to_city == to_city,
            )
        )
        return list(result.scalars().all())

    async def count_by_client(self, client_telegram_id: int) -> int:
        result = await self.session.execute(
            select(func.count(ShipmentRequest.id)).where(
                ShipmentRequest.client_telegram_id == client_telegram_id
            )
        )
        return int(result.scalar() or 0)

    async def get_request_by_id(self, request_id: int) -> Optional[ShipmentRequest]:
        res = await self.session.execute(
            select(ShipmentRequest).where(ShipmentRequest.id == request_id)
        )
        return res.scalar_one_or_none()

    async def get_client_and_request(
        self, telegram_id: int, request_id: int
    ) -> Tuple[Optional[Client], Optional[ShipmentRequest]]:
        client = await self.session.get(Client, telegram_id, identity_token=None)
        # ↑ якщо telegram_id не є PK — використай:
        # client = (await self.session.execute(select(Client).where(Client.telegram_id == telegram_id))).scalar_one_or_none()
        req = await self.get_request_by_id(request_id)
        return client, req

    async def create_batch(self, requests_data: List[dict]) -> List[ShipmentRequest]:
        """Створити кілька заявок одночасно"""
        requests = [ShipmentRequest(**data) for data in requests_data]
        self.session.add_all(requests)
        await self.session.commit()
        return requests

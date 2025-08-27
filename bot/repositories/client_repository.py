from bot.repositories.base import BaseRepository
from bot.models.client import Client
from typing import Optional, List
from sqlalchemy import select, update


class ClientRepository(BaseRepository[Client]):
    def __init__(self, session):
        super().__init__(session, Client)

    async def find_by_phone(self, phone: str) -> Optional[Client]:
        """Пошук за телефоном"""
        result = await self.session.execute(select(Client).where(Client.phone == phone))
        return result.scalar_one_or_none()

    async def find_by_email(self, email: str) -> Optional[Client]:
        """Пошук за email"""
        if not email:
            return None
        result = await self.session.execute(select(Client).where(Client.email == email))
        return result.scalar_one_or_none()

    async def is_registered(self, telegram_id: int) -> bool:
        """Перевірка реєстрації"""
        client = await self.get_by_telegram_id(telegram_id)
        return client is not None

    async def get_verified_clients(self) -> List[Client]:
        """Отримати верифікованих клієнтів"""
        result = await self.session.execute(select(Client).where(Client.is_verified))
        return list(result.scalars().all())

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[Client]:
        """Пошук клієнта за telegram_id"""
        result = await self.session.execute(
            select(Client).where(Client.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

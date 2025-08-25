# bot/repositories/client_repository.py
"""
Репозиторій для клієнтів - наслідує базовий репозиторій
"""

from bot.repositories.base import BaseRepository
from bot.models.client import Client
from typing import Optional, List
from sqlalchemy import select


class ClientRepository(BaseRepository[Client]):
    """
    Специфічний репозиторій для роботи з клієнтами.
    Наслідування дозволяє:
    1. Отримати всі методи з BaseRepository
    2. Додати специфічні методи тільки для Client
    """
    
    def __init__(self, session):
        super().__init__(Client, session)  # Викликаємо конструктор батьківського класу
    
    async def find_by_phone(self, phone: str) -> Optional[Client]:
        """Метод специфічний тільки для клієнтів"""
        result = await self.session.execute(
            select(Client).where(Client.phone == phone)
        )
        return result.scalar_one_or_none()
    
    async def is_registered(self, telegram_id: int) -> bool:
        """Перевірка чи зареєстрований клієнт"""
        client = await self.get_by_telegram_id(telegram_id)
        return client is not None



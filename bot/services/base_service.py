"""
Базовий сервіс - містить спільну логіку для всіх сервісів
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.database import async_session
import logging

logger = logging.getLogger(__name__)


class BaseService:
    """
    Базовий клас для всіх сервісів.
    Сервіс = бізнес-логіка вашого додатку.
    
    Принципи ООП тут:
    1. Інкапсуляція - логіка схована всередині класу
    2. Наслідування - всі сервіси матимуть ці методи
    3. Поліморфізм - можна перевизначати методи в нащадках
    """
    
    def __init__(self):
        self._session: Optional[AsyncSession] = None
    
    async def __aenter__(self):
        """Магічний метод для async with"""
        self._session = async_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закриває сесію після використання"""
        if self._session:
            await self._session.close()
    
    @property
    def session(self) -> AsyncSession:
        """Геттер для сесії (property decorator - це ООП pattern)"""
        if not self._session:
            raise RuntimeError("Service used outside of async context")
        return self._session
    
    async def handle_error(self, error: Exception, context: str = ""):
        """Централізована обробка помилок"""
        logger.error(f"Error in {context}: {error}")
        # Тут можна додати Sentry або інший моніторинг
        raise
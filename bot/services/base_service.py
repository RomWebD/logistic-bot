"""
Базовий сервіс - спільна логіка для всіх сервісів
"""

import logging
from typing import Optional, TypeVar, Generic

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from contextlib import AsyncExitStack

from bot.database.database import get_session

logger = logging.getLogger(__name__)

T = TypeVar("T")  # для типізації методів (generic add/get)


class BaseService(Generic[T]):
    """
    Базовий клас для всіх сервісів.
    Використовується як контекстний менеджер:

    async with SomeService() as svc:
        obj = await svc.get_by_id(Model, 1)
        await svc.commit()
    """

    def __init__(self):
        self._stack: Optional[AsyncExitStack] = None
        self._session: Optional[AsyncSession] = None

    async def __aenter__(self):
        self._stack = AsyncExitStack()
        await self._stack.__aenter__()
        self._session = await self._stack.enter_async_context(get_session())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._stack:
            await self._stack.__aexit__(exc_type, exc_val, exc_tb)

    # ---------------- Core API ----------------

    @property
    def session(self) -> AsyncSession:
        if not self._session:
            raise RuntimeError("Service used outside of async context")
        return self._session

    async def add(self, obj: T, commit: bool = False) -> T:
        """Додає об’єкт у сесію, опціонально одразу комітить"""
        self.session.add(obj)
        if commit:
            await self.commit()
        return obj

    async def get_by_id(self, model: type[T], obj_id: int) -> Optional[T]:
        """Універсальний пошук за ID"""
        res = await self.session.execute(select(model).where(model.id == obj_id))
        return res.scalar_one_or_none()

    async def commit(self):
        """Фіналізує транзакцію"""
        try:
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Commit failed: {e}")
            raise

    async def rollback(self):
        """Відкат транзакції"""
        await self.session.rollback()

    async def flush(self):
        """Флашить pending-об’єкти у БД (без коміту)"""
        await self.session.flush()

    async def handle_error(self, error: Exception, context: str = ""):
        """Централізована обробка помилок"""
        logger.error(f"Error in {context}: {error}")
        raise

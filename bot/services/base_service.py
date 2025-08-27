# bot/services/base_service.py
import logging
from typing import Optional, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from contextlib import AsyncExitStack

from bot.database.database import get_session

logger = logging.getLogger(__name__)
T = TypeVar("T")

class BaseService(Generic[T]):
    """
    Працює в двох режимах:
    1) Зовнішня сесія передана у конструктор → сервіс НЕ керує її життєвим циклом.
    2) Сесію не передали → можна `async with Service()` і він сам відкриє/закриє сесію.
    """

    def __init__(self, session: Optional[AsyncSession] = None):
        self._stack: Optional[AsyncExitStack] = None
        self._session: Optional[AsyncSession] = session
        self._owns_session: bool = session is None  # чи ми самі відкривали сесію

    async def __aenter__(self):
        self._stack = AsyncExitStack()
        await self._stack.__aenter__()
        if self._session is None:
            # відкриваємо свою сесію лише якщо її не передали
            self._session = await self._stack.enter_async_context(get_session())
            self._owns_session = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._stack:
            await self._stack.__aexit__(exc_type, exc_val, exc_tb)

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("Service used outside of async context and without session")
        return self._session

    async def add(self, obj: T, commit: bool = False) -> T:
        self.session.add(obj)
        if commit:
            await self.commit()
        return obj

    async def get_by_id(self, model: type[T], obj_id: int) -> Optional[T]:
        res = await self.session.execute(select(model).where(model.id == obj_id))
        return res.scalar_one_or_none()

    async def commit(self):
        try:
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Commit failed: {e}")
            raise

    async def rollback(self):
        await self.session.rollback()

    async def flush(self):
        await self.session.flush()

    async def handle_error(self, error: Exception, context: str = ""):
        logger.error(f"Error in {context}: {error}")
        raise

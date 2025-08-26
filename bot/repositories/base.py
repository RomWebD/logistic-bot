from typing import TypeVar, Generic, Type, Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Базовий клас для всіх репозиторіїв"""

    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.model = model
        self.session = session

    async def create(self, **kwargs) -> ModelType:
        """Створити новий запис"""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Отримати запис за ID"""
        return await self.session.get(self.model, id)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[ModelType]:
        """Отримати запис за Telegram ID"""
        if not hasattr(self.model, "telegram_id"):
            return None
        result = await self.session.execute(
            select(self.model).where(self.model.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[ModelType]:
        """Отримати всі записи"""
        result = await self.session.execute(select(self.model))
        return list(result.scalars().all())

    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Оновити запис"""
        instance = await self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            await self.session.commit()
            await self.session.refresh(instance)
        return instance

    async def delete(self, id: int) -> bool:
        """Видалити запис"""
        instance = await self.get_by_id(id)
        if instance:
            await self.session.delete(instance)
            await self.session.commit()
            return True
        return False

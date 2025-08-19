from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os
from collections.abc import AsyncGenerator  # Python 3.10+
from contextlib import asynccontextmanager
from sqlalchemy.pool import NullPool

DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite+aiosqlite:///./local.db"
)  # default SQLite

engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=NullPool,  # важливо для SQLite
    future=True,
)
async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,  # щоб дані не зникали після commit()
)


class Base(DeclarativeBase):
    pass


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для отримання асинхронної сесії.
    Використовується в сервісах / репозиторіях / CRUD.

    Yields:
        AsyncSession: відкрита сесія до БД
    """
    async with async_session_maker() as session:
        yield session

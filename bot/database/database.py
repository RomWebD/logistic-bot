from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os
from collections.abc import AsyncGenerator  # Python 3.10+

DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite+aiosqlite:///./local.db"
)  # default SQLite

engine = create_async_engine(DATABASE_URL, echo=True, pool_pre_ping=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

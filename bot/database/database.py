import os
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool
import logging

logger = logging.getLogger(__name__)


# Конфігурація з environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./local.db")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # development | production
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))  # Розмір пулу
DB_MAX_OVERFLOW = int(
    os.getenv("DB_MAX_OVERFLOW", "40")
)  # Максимум додаткових з'єднань
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))  # Таймаут очікування
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))  # Час життя з'єднання


def create_engine() -> AsyncEngine:
    """
    Створює engine з правильними налаштуваннями для різних БД
    """

    # Визначаємо тип БД
    is_sqlite = "sqlite" in DATABASE_URL
    is_postgresql = "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL

    # Базові параметри
    engine_params = {
        "echo": ENVIRONMENT == "development",  # SQL логи тільки в dev
        "future": True,
    }

    # Налаштування для SQLite (development)
    if is_sqlite:
        engine_params.update(
            {
                "connect_args": {"check_same_thread": False},
                "poolclass": NullPool,  # Для SQLite це ок
            }
        )
        logger.info("Using SQLite with NullPool")

    # Налаштування для PostgreSQL (production)
    elif is_postgresql:
        engine_params.update(
            {
                "poolclass": AsyncAdaptedQueuePool,  # Правильний pool для async
                "pool_size": DB_POOL_SIZE,  # Кількість постійних з'єднань
                "max_overflow": DB_MAX_OVERFLOW,  # Додаткові з'єднання при навантаженні
                "pool_timeout": DB_POOL_TIMEOUT,  # Скільки чекати вільне з'єднання
                "pool_recycle": DB_POOL_RECYCLE,  # Перествоювати з'єднання кожну годину
                "pool_pre_ping": True,  # Перевіряти з'єднання перед використанням
            }
        )
        logger.info(
            f"Using PostgreSQL with pool_size={DB_POOL_SIZE}, "
            f"max_overflow={DB_MAX_OVERFLOW}"
        )

    # Для інших БД (MySQL, etc)
    else:
        engine_params.update(
            {
                "poolclass": AsyncAdaptedQueuePool,
                "pool_size": 10,
                "max_overflow": 20,
            }
        )

    return create_async_engine(DATABASE_URL, **engine_params)


# Створюємо engine
engine = create_engine()

# Session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Дані доступні після commit
    autoflush=False,  # Не flush автоматично (контроль в руках)
    autocommit=False,  # Явні транзакції
)

# Для Middleware підходу (який я показував)
async_session_maker = async_session  # Alias для сумісності


# База для моделей
class Base(DeclarativeBase):
    pass


# Context manager для сесії
@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager для роботи з сесією
    Автоматично закриває сесію після використання
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()  # Auto-commit якщо все ок
        except Exception:
            await session.rollback()  # Rollback при помилці
            raise
        finally:
            await session.close()  # Завжди закриваємо


# Для DI підходу - функція без context manager
async def get_db_session() -> AsyncSession:
    """
    Проста функція для DI (Dependency Injection)
    Використовується в middleware
    """
    return async_session()


# Функції для управління БД
async def init_db():
    """Створити всі таблиці"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


async def drop_db():
    """Видалити всі таблиці (обережно!)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.info("Database tables dropped")


async def close_db():
    """Закрити всі з'єднання (при shutdown)"""
    await engine.dispose()
    logger.info("Database connections closed")


# Health check для моніторингу
async def check_db_connection() -> bool:
    """
    Перевірка з'єднання з БД
    Використовується для health checks в production
    """
    try:
        async with get_session() as session:
            await session.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

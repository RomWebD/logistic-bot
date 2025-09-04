from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

# Імпортуємо з оновленого database.py
from bot.database.database import async_session
from bot.repositories.client_repository import ClientRepository
from bot.repositories.carrier_repository import CarrierCompanyRepository
from bot.repositories.shipment_repository import ShipmentRepository
from bot.repositories.google_sheet_repository import GoogleSheetRepository
import logging

logger = logging.getLogger(__name__)


class RepositoryMiddleware(BaseMiddleware):
    """
    Розширений middleware який створює не тільки сесію, а й репозиторії
    Для зручності - всі репозиторії одразу доступні в handler'ах
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        Створює сесію та всі репозиторії
        """

        async with async_session() as session:
            # Додаємо сесію
            data["session"] = session

            # Створюємо репозиторії з цією сесією
            data["client_repo"] = ClientRepository(session)
            data["carrier_repo"] = CarrierCompanyRepository(session)
            data["shipment_repo"] = ShipmentRepository(session)
            data["sheet_repo"] = GoogleSheetRepository(session)

            try:
                result = await handler(event, data)
                await session.commit()
                return result

            except Exception as e:
                await session.rollback()
                logger.error(f"Repository middleware error: {e}")
                raise

# bot/services/verification_client.py
from enum import Enum
from sqlalchemy import select
from bot.database.database import get_session
from bot.models.client import Client
# from bot.models import Client


class ClientStatus(Enum):
    NOT_REGISTERED = "not_registered"
    NOT_VERIFIED = "not_verified"
    VERIFIED = "verified"


async def get_client_status(telegram_id: int) -> ClientStatus:
    async with get_session() as session:
        client = await session.scalar(
            select(Client).where(Client.telegram_id == telegram_id)
        )
        if not client:
            return ClientStatus.NOT_REGISTERED
        if client.is_verify:
            return ClientStatus.VERIFIED
        return ClientStatus.NOT_VERIFIED

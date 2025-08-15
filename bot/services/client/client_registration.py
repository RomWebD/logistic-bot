# bot/services/client/client_registration.py
from sqlalchemy import select
from bot.database.database import async_session
from bot.models import Client  
from bot.schemas.client import ClientRegistrationData


async def check_existing_client(telegram_id: int) -> bool:
    async with async_session() as session:
        existing = await session.scalar(
            select(Client).where(Client.telegram_id == telegram_id)
        )
        return bool(existing)


async def register_new_client(data: ClientRegistrationData) -> bool:
    async with async_session() as session:
        # Перевірка дубля по телефону/емейлу
        exists = await session.scalar(
            select(Client).where(
                (Client.phone == data.phone) | (Client.email == data.email)
            )
        )
        if exists:
            return False

        # Pydantic v2 -> .model_dump()
        payload = data.model_dump(mode="json")
        payload["is_verify"] = False
        client = Client(**payload)
        session.add(client)
        await session.commit()
        return True

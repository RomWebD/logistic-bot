# bot/repositories/client_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.models import Client, OwnershipEnum
from bot.schemas.client import ClientRegistrationFull


class ClientRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram(self, telegram_id: int) -> Client | None:
        res = await self.session.execute(
            select(Client).where(Client.telegram_id == telegram_id)
        )
        return res.scalar_one_or_none()

    async def create_or_update(self, data: ClientRegistrationFull) -> Client:
        obj = await self.get_by_telegram(data.telegram_id)
        if obj is None:
            obj = Client(telegram_id=data.telegram_id)

        obj.full_name = data.full_name
        obj.company_name = data.company_name

        obj.tax_id = data.tax_id
        obj.phone = data.phone
        obj.email = data.email
        obj.address = data.address
        obj.website = str(data.website) if data.website else None

        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

from sqlalchemy import select
from bot.models.carrier_company import CarrierCompany
from bot.database.database import get_session
from enum import Enum


class CarrierStatus(Enum):
    NOT_REGISTERED = "not_registered"
    NOT_VERIFIED = "not_verified"
    VERIFIED = "verified"


async def get_carrier_status(telegram_id: int) -> CarrierStatus:
    async with get_session() as session:
        carrier = await session.scalar(
            select(CarrierCompany).where(CarrierCompany.telegram_id == telegram_id)
        )
        if not carrier:
            return CarrierStatus.NOT_REGISTERED
        if carrier.is_verify:
            return CarrierStatus.VERIFIED
        return CarrierStatus.NOT_VERIFIED


async def is_verified_carrier(chat_id: int) -> bool:
    async with get_session() as session:
        result = await session.scalar(
            select(CarrierCompany).where(
                CarrierCompany.telegram_id == chat_id,
                CarrierCompany.is_verify.is_(True),
            )
        )
        return result is not None


async def get_carrier_by_telegram_id(telegram_id: int) -> CarrierCompany | None:
    async with get_session() as session:
        return await session.scalar(
            select(CarrierCompany).where(CarrierCompany.telegram_id == telegram_id)
        )


async def delete_carrier_by_telegram_id(telegram_id: int, callback) -> bool:
    async with get_session() as session:
        carrier = await session.scalar(
            select(CarrierCompany).where(CarrierCompany.telegram_id == telegram_id)
        )
        if not carrier:
            await callback.message.answer("❌ Ваш профіль не знайдено.")

            return False

        await session.delete(carrier)
        await session.commit()
        await callback.message.answer("✅ Ваш профіль успішно видалено.")

        return True

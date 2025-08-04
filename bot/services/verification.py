from sqlalchemy import select
from bot.models.carrier_company import CarrierCompany
from bot.database.database import async_session


async def is_verified_carrier(chat_id: int) -> bool:
    async with async_session() as session:
        result = await session.scalar(
            select(CarrierCompany).where(
                CarrierCompany.telegram_id == chat_id,
                CarrierCompany.is_verify.is_(True),
            )
        )
        return result is not None


async def get_carrier_by_telegram_id(telegram_id: int) -> CarrierCompany | None:
    async with async_session() as session:
        return await session.scalar(
            select(CarrierCompany).where(CarrierCompany.telegram_id == telegram_id)
        )


async def delete_carrier_by_telegram_id(telegram_id: int, callback) -> bool:
    async with async_session() as session:
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

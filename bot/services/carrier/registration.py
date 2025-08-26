from bot.schemas.carrier.carrier import CarrierRegistrationData, CarrierResponse
from bot.repositories.carrier_repository import CarrierRepository
from typing import Dict, Any


class CarrierRegistrationService:
    """Сервіс для реєстрації та управління перевізниками"""

    def __init__(self, session):
        self.session = session
        self.repository = CarrierRepository(session)

    async def register(self, data: CarrierRegistrationData) -> Dict[str, Any]:
        """Реєстрація нового перевізника"""

        # Перевірка на існування
        existing = await self.repository.get_by_telegram_id(data.telegram_id)
        if existing:
            return {"success": False, "message": "Перевізник вже зареєстрований"}

        # Перевірка унікальності email
        if await self.repository.find_by_email(data.email):
            return {"success": False, "message": "Email вже використовується"}

        # Перевірка унікальності ЄДРПОУ
        if await self.repository.find_by_tax_id(data.tax_id):
            return {
                "success": False,
                "message": "Компанія з таким ЄДРПОУ вже зареєстрована",
            }

        # Створення перевізника
        carrier = await self.repository.create(**data.model_dump())
        await self.session.commit()

        # Формуємо відповідь
        response = CarrierResponse.model_validate(carrier)

        return {
            "success": True,
            "carrier": response,
            "message": "Реєстрація успішна. Очікуйте верифікації.",
        }

    async def verify(self, carrier_id: int) -> bool:
        """Верифікація перевізника"""
        carrier = await self.repository.get_by_id(carrier_id)
        if not carrier:
            return False

        carrier.is_verified = True
        await self.session.commit()
        return True

    async def update(self, telegram_id: int, data: dict) -> Dict[str, Any]:
        """Оновлення даних перевізника"""
        carrier = await self.repository.get_by_telegram_id(telegram_id)
        if not carrier:
            return {"success": False, "message": "Перевізник не знайдений"}

        # Оновлюємо тільки передані поля
        for key, value in data.items():
            if value is not None and hasattr(carrier, key):
                setattr(carrier, key, value)

        await self.session.commit()

        return {"success": True, "carrier": CarrierResponse.model_validate(carrier)}

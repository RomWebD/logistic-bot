"""
Сервіс для заявок - найскладніша бізнес-логіка
"""

from bot.services.base_service import BaseService
from bot.repositories.shipment_repository import ShipmentRepository
from bot.repositories.carrier_repository import CarrierCompanyRepository
from bot.repositories.client_repository import ClientRepository
from bot.models.shipment_request import Shipment_request
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ShipmentStatus(Enum):
    """Enum - це ООП спосіб зберігати константи"""

    DRAFT = "draft"
    PUBLISHED = "published"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class ShipmentCreateData:
    """DTO для створення заявки"""

    client_telegram_id: int
    route: str
    date: str  # Буде парситись через Groq
    cargo_type: str
    volume: str
    weight: str
    loading: str
    unloading: str
    price: str
    description: Optional[str] = None


class ShipmentService(BaseService):
    """
    Сервіс для управління заявками.
    Композиція - використовуємо інші репозиторії.
    """

    async def shipment(self, data: ShipmentCreateData) -> Dict[str, Any]:
        """Створення нової заявки з валідацією"""
        try:
            # Перевірка клієнта
            client_repo = ClientRepository(self.session)
            client = await client_repo.get_by_telegram_id(data.client_telegram_id)

            if not client:
                return {
                    "success": False,
                    "message": "❌ Спочатку потрібно зареєструватись як клієнт",
                }

            # Валідація даних
            validation_result = self._validate_shipment_data(data)
            if not validation_result["valid"]:
                return {"success": False, "message": validation_result["message"]}

            # Створення заявки
            shipment_repo = ShipmentRepository(self.session)
            shipment = await shipment_repo.create(
                client_telegram_id=data.client_telegram_id,
                route=data.route,
                date=data.date,  # Groq parser в моделі
                cargo_type=data.cargo_type,
                volume=data.volume,
                weight=data.weight,
                loading=data.loading,
                unloading=data.unloading,
                price=data.price,
                description=data.description,
            )

            await self.session.commit()

            # Знаходимо підходящих перевізників
            carriers = await self._find_matching_carriers(shipment)

            return {
                "success": True,
                "message": "✅ Заявка створена",
                "shipment": shipment,
                "matching_carriers": carriers,
            }

        except Exception as e:
            await self.session.rollback()
            await self.handle_error(e, "ShipmentService.create_shipment")
            return {"success": False, "message": "⚠️ Помилка створення заявки"}

    async def get_client_shipments(self, telegram_id: int) -> List[Shipment_request]:
        """Отримати всі заявки клієнта"""
        repo = ShipmentRepository(self.session)
        return await repo.get_by_client(telegram_id)

    async def get_shipments_for_carrier(
        self, carrier_telegram_id: int
    ) -> List[Shipment_request]:
        """Знайти підходящі заявки для перевізника"""
        carrier_repo = CarrierCompanyRepository(self.session)
        carrier = await carrier_repo.get_by_telegram_id(carrier_telegram_id)

        if not carrier:
            return []

        shipment_repo = ShipmentRepository(self.session)
        # Знаходимо заявки по маршруту перевізника
        return await shipment_repo.get_by_route(carrier.route)

    async def accept_shipment(
        self, shipment_id: int, carrier_telegram_id: int
    ) -> Dict[str, Any]:
        """Прийняти заявку перевізником"""
        # Тут буде логіка прийняття заявки
        # Поки що заглушка
        return {"success": True, "message": "Заявка прийнята"}

    def _validate_shipment_data(self, data: ShipmentCreateData) -> Dict[str, Any]:
        """Приватний метод валідації"""
        # Перевірка маршруту
        if len(data.route) < 5:
            return {"valid": False, "message": "❌ Маршрут занадто короткий"}

        # Перевірка ціни
        try:
            price = int("".join(filter(str.isdigit, data.price)))
            if price < 100:
                return {"valid": False, "message": "❌ Ціна занадто низька"}
        except Exception as err:
            print(err)
            return {"valid": False, "message": "❌ Невірний формат ціни"}

        return {"valid": True, "message": "OK"}

    async def _find_matching_carriers(self, shipment: Shipment_request) -> List[Any]:
        """Знайти підходящих перевізників"""
        carrier_repo = CarrierRepository(self.session)
        # Шукаємо перевізників з подібним маршрутом
        carriers = await carrier_repo.find_by_route(shipment.route.split("→")[0])
        return carriers

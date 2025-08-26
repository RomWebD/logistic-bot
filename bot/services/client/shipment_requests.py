from bot.schemas.client.shipment import ShipmentRequestCreateData
from bot.repositories.shipment_repository import ShipmentRepository
from bot.services.base_service import BaseService
from bot.services.external.groq import normalize_date_with_groq
from typing import Dict, Any


class ShipmentService(BaseService):
    def __init__(self, session):
        self.session = session
        self.repository = ShipmentRepository(self.session)

    async def create_shipment(self, data: ShipmentRequestCreateData) -> Dict[str, Any]:
        # Парсимо дату через AI якщо потрібно
        if not data.date and data.date_text:
            data.date = normalize_date_with_groq(data.date_text)
            if not data.date:
                return {"success": False, "message": "Не вдалось розпізнати дату"}

        # Використовуємо репозиторій для створення
        shipment = await self.repository.create(
            client_telegram_id=data.client_telegram_id,
            from_city=data.from_city,
            to_city=data.to_city,
            date=data.date,
            date_text=data.date_text,
            cargo_type=data.cargo_type,
            weight=data.weight,
            volume=data.volume,
            loading=data.loading,
            unloading=data.unloading,
            price=data.price,  # Тепер як string з валютою
            description=data.description,
        )

        return {"success": True, "shipment": shipment}

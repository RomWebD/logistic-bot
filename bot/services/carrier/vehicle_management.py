from bot.repositories.carrier_repository import CarrierRepository
from bot.models.transport_vehicle import TransportVehicle
from typing import Dict, Any, List


class VehicleManagementService:
    """Управління автопарком"""

    def __init__(self, session):
        self.session = session
        self.carrier_repo = CarrierRepository(session)

    async def add_vehicle(
        self, carrier_telegram_id: int, vehicle_data: dict
    ) -> Dict[str, Any]:
        """Додати транспортний засіб"""

        # Перевірка перевізника
        carrier = await self.carrier_repo.get_by_telegram_id(carrier_telegram_id)
        if not carrier:
            return {"success": False, "message": "Перевізник не знайдений"}

        if not carrier.is_verified:
            return {"success": False, "message": "Спочатку пройдіть верифікацію"}

        # Створення транспорту
        vehicle = TransportVehicle(carrier_company_id=carrier.id, **vehicle_data)

        self.session.add(vehicle)
        await self.session.commit()

        return {"success": True, "vehicle": vehicle, "message": "Транспорт додано"}

    async def get_carrier_vehicles(
        self, carrier_telegram_id: int
    ) -> List[TransportVehicle]:
        """Отримати весь транспорт перевізника"""

        carrier = await self.carrier_repo.get_by_telegram_id(carrier_telegram_id)
        if not carrier:
            return []

        return carrier.vehicles

    async def update_vehicle(
        self, carrier_telegram_id: int, vehicle_id: int, update_data: dict
    ) -> Dict[str, Any]:
        """Оновити дані транспорту"""

        carrier = await self.carrier_repo.get_by_telegram_id(carrier_telegram_id)
        if not carrier:
            return {"success": False, "message": "Перевізник не знайдений"}

        # Перевірка що транспорт належить цьому перевізнику
        vehicle = next((v for v in carrier.vehicles if v.id == vehicle_id), None)

        if not vehicle:
            return {"success": False, "message": "Транспорт не знайдений"}

        # Оновлення
        for key, value in update_data.items():
            if hasattr(vehicle, key):
                setattr(vehicle, key, value)

        await self.session.commit()

        return {"success": True, "vehicle": vehicle}

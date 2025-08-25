"""
Сервіс для роботи з клієнтами - вся бізнес-логіка тут
"""

from bot.services.base_service import BaseService
from bot.repositories.client_repository import ClientRepository
from bot.models.client import Client
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class ClientRegistrationData:
    """
    Data Transfer Object (DTO) - це патерн для передачі даних.
    Замість передавати купу параметрів, передаємо один об'єкт.
    """
    telegram_id: int
    full_name: str
    phone: str


class ClientService(BaseService):
    """
    Сервіс для клієнтів.
    Тут вся логіка: валідація, перевірки, бізнес-правила.
    """
    
    async def register_client(self, data: ClientRegistrationData) -> Dict[str, Any]:
        """
        Реєстрація клієнта з усіма перевірками.
        Повертаємо словник з результатом для гнучкості.
        """
        try:
            repo = ClientRepository(self.session)
            
            # Перевірка на існуючого клієнта
            existing = await repo.get_by_telegram_id(data.telegram_id)
            if existing:
                return {
                    "success": False,
                    "message": "🔁 Ви вже зареєстровані як клієнт",
                    "client": existing
                }
            
            # Валідація телефону
            if not self._validate_phone(data.phone):
                return {
                    "success": False,
                    "message": "❌ Невірний формат телефону. Використовуйте: +380XXXXXXXXX"
                }
            
            # Створення клієнта
            client = await repo.create(
                telegram_id=data.telegram_id,
                full_name=data.full_name,
                phone=data.phone
            )
            
            await self.session.commit()
            
            return {
                "success": True,
                "message": "✅ Реєстрація успішна!",
                "client": client
            }
            
        except Exception as e:
            await self.session.rollback()
            await self.handle_error(e, "ClientService.register_client")
            return {
                "success": False,
                "message": "⚠️ Помилка реєстрації. Спробуйте пізніше."
            }
    
    async def get_client(self, telegram_id: int) -> Optional[Client]:
        """Отримати клієнта за telegram_id"""
        repo = ClientRepository(self.session)
        return await repo.get_by_telegram_id(telegram_id)
    
    async def update_client_info(self, telegram_id: int, **kwargs) -> bool:
        """Оновити інформацію клієнта"""
        repo = ClientRepository(self.session)
        client = await repo.get_by_telegram_id(telegram_id)
        
        if not client:
            return False
        
        await repo.update(client.id, **kwargs)
        await self.session.commit()
        return True
    
    def _validate_phone(self, phone: str) -> bool:
        """Приватний метод для валідації (підкреслення = приватний)"""
        # Просте правило для українських номерів
        cleaned = ''.join(filter(str.isdigit, phone))
        return len(cleaned) in [10, 12] and (
            cleaned.startswith('380') or cleaned.startswith('0')
        )
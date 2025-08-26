"""
Сервіс реєстрації клієнтів
"""

from bot.services.base_service import BaseService
from bot.repositories.client_repository import ClientRepository
from bot.schemas.client import ClientRegistrationData, ClientResponse
from bot.models.client import Client
from typing import Optional, Dict, Any

from bot.services.client.verification_client import ClientStatus


class ClientRegistrationService(BaseService):
    """
    Сервіс для реєстрації та верифікації клієнтів
    """

    def __init__(self, session):
        super().__init__(session)
        self.repo = ClientRepository(session)

    async def check_existing(self, telegram_id: int) -> Optional[Client]:
        """Перевірка чи існує клієнт"""
        return await self.repo.get_by_telegram_id(telegram_id)

    async def register(self, data: ClientRegistrationData) -> Dict[str, Any]:
        """
        Повна реєстрація з валідацією
        Повертає словник для гнучкості
        """
        try:
            # Перевірка дублікатів
            if await self.repo.get_by_telegram_id(data.telegram_id):
                return {
                    "success": False,
                    "message": "Клієнт вже зареєстрований",
                    "code": "CLIENT_EXISTS",
                }

            if await self.find_by_email(data.email):
                return {
                    "success": False,
                    "message": "Email вже використовується",
                    "code": "EMAIL_EXISTS",
                }

            # Створення клієнта
            client = await self.create(**data.model_dump())
            await self.session.commit()

            # Конвертуємо в Pydantic схему для відповіді
            response = ClientResponse.model_validate(client)

            return {
                "success": True,
                "message": "Реєстрація успішна",
                "client": response.model_dump(),
            }

        except Exception as e:
            await self.session.rollback()
            self.handle_error(e, "register")
            return {
                "success": False,
                "message": "Помилка реєстрації",
                "code": "REGISTRATION_ERROR",
            }

    async def verify_client(self, client_id: int) -> bool:
        """Верифікація клієнта адміністратором"""
        client = await self.repo.get_by_id(client_id)

        if not client:
            return False

        client.is_verify = True
        await self.session.commit()

        # Тут можна додати відправку повідомлення клієнту
        return True

    async def get_status(self, telegram_id: int) -> ClientStatus:
        client = await self.repo.get_by_telegram_id(telegram_id)
        if not client:
            return ClientStatus.NOT_REGISTERED
        return ClientStatus(client.status)

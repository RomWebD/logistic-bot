# bot/services/client/registration.py
from typing import Optional, Dict, Any
from bot.services.base_service import BaseService
from bot.repositories.client_repository import ClientRepository
from bot.schemas.client import ClientRegistrationData, ClientResponse
from bot.models.client import Client
from bot.services.client.verification_client import ClientStatus

class ClientRegistrationService(BaseService[Client]):
    """
    Сервіс для реєстрації та верифікації клієнтів
    """

    def __init__(self, session: Optional["AsyncSession"] = None):
        super().__init__(session)

    @property
    def repo(self) -> ClientRepository:
        # Лінива ініціалізація на основі поточної сесії
        return ClientRepository(self.session)

    async def check_existing(self, telegram_id: int) -> Optional[Client]:
        return await self.repo.get_by_telegram_id(telegram_id)

    async def register(self, data: ClientRegistrationData) -> Dict[str, Any]:
        try:
            if await self.repo.get_by_telegram_id(data.telegram_id):
                return {"success": False, "message": "Клієнт вже зареєстрований", "code": "CLIENT_EXISTS"}

            if await self.repo.find_by_email(data.email):
                return {"success": False, "message": "Email вже використовується", "code": "EMAIL_EXISTS"}

            client = await self.repo.create(**data.model_dump())
            await self.session.commit()

            response = ClientResponse.model_validate(client)
            return {"success": True, "message": "Реєстрація успішна", "client": response.model_dump()}

        except Exception as e:
            await self.session.rollback()
            await self.handle_error(e, "register")
            return {"success": False, "message": "Помилка реєстрації", "code": "REGISTRATION_ERROR"}

    async def verify_client(self, client_id: int) -> bool:
        client = await self.repo.get_by_id(client_id)
        if not client:
            return False
        # вирівняй з реальною моделлю: is_verified vs is_verify
        client.is_verified = True
        await self.session.commit()
        return True

    async def get_status(self, telegram_id: int) -> ClientStatus:
        client = await self.repo.get_by_telegram_id(telegram_id)
        if not client:
            return ClientStatus.NOT_REGISTERED
        return ClientStatus(client.status)

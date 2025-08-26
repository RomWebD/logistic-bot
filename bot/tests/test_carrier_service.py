import pytest
from unittest.mock import AsyncMock, MagicMock
from bot.services.carrier_service import CarrierService


@pytest.mark.asyncio
async def test_get_vehicles_sheet_url_verified():
    """Тест: верифікований перевізник отримує URL"""
    
    # Створюємо мок сесії
    mock_session = AsyncMock()
    
    # Створюємо сервіс
    service = CarrierService(mock_session)
    
    # Мокаємо репозиторії
    mock_carrier = MagicMock()
    mock_carrier.is_verified = True
    service.carrier_repo.get_by_telegram_id = AsyncMock(return_value=mock_carrier)
    
    mock_binding = MagicMock()
    mock_binding.sheet_url = "https://sheets.google.com/123"
    service.sheet_repo.get_by_owner_and_type = AsyncMock(return_value=mock_binding)
    
    # Тестуємо
    result = await service.get_vehicles_sheet_url(123456)
    
    # Перевіряємо
    assert result == "https://sheets.google.com/123"
    service.carrier_repo.get_by_telegram_id.assert_called_once_with(123456)


@pytest.mark.asyncio  
async def test_get_vehicles_sheet_url_not_verified():
    """Тест: неверифікований перевізник не отримує URL"""
    
    mock_session = AsyncMock()
    service = CarrierService(mock_session)
    
    # Мокаємо неверифікованого перевізника
    mock_carrier = MagicMock()
    mock_carrier.is_verified = False
    service.carrier_repo.get_by_telegram_id = AsyncMock(return_value=mock_carrier)
    
    # Тестуємо
    result = await service.get_vehicles_sheet_url(123456)
    
    # Перевіряємо що повернув None
    assert result is None
    # І що не викликав sheet_repo (бізнес-правило!)
    service.sheet_repo.get_by_owner_and_type.assert_not_called()
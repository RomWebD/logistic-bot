"""
Валідатори для форм використовують PhoneService
"""

from typing import Optional
from bot.utils.phone import PhoneService
import re


def validate_phone_field(value: str, country: str = "UA") -> Optional[str]:
    """
    Валідатор для FormField
    Повертає помилку або None
    """
    if not value:
        return "Телефон обов'язковий"

    is_valid, formatted, error = PhoneService.parse_and_validate(value, country)

    if not is_valid:
        return error

    return None


def normalize_phone_field(value: str, country: str = "UA") -> str:
    """
    Normalizer для FormField
    Повертає нормалізований номер
    """
    is_valid, formatted, _ = PhoneService.parse_and_validate(value, country)

    if is_valid and formatted:
        return formatted

    # Якщо не вдалось - повертаємо очищений
    return PhoneService._clean_number(value)


def validate_email(value: str) -> Optional[str]:
    """Валідатор email для форми"""
    if not value:
        return "Email обов'язковий"

    # Простий regex для email
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(pattern, value.strip()):
        return "Невірний формат email. Приклад: name@example.com"

    return None


def validate_price(value: str) -> Optional[str]:
    """Валідатор ціни"""
    try:
        # Намагаємось витягти число
        digits = re.sub(r"[^\d.]", "", value)
        price = float(digits)

        if price <= 0:
            return "Ціна має бути більше нуля"

        return None
    except:
        return "Невірний формат ціни. Введіть число"


def validate_date(value: str) -> Optional[str]:
    """Валідатор дати - просто перевіряємо що щось введено"""
    if not value or len(value) < 3:
        return "Введіть дату. Наприклад: завтра о 14:00"
    return None


def validate_tax_id(value: str) -> Optional[str]:
    """Валідатор ЄДРПОУ/ІПН для форми"""
    if not value:
        return "ЄДРПОУ/ІПН обов'язковий"

    # Тільки цифри
    digits = re.sub(r"\D", "", value)

    if len(digits) == 8:
        return None  # OK - ЄДРПОУ
    elif len(digits) == 10:
        return None  # OK - ІПН
    else:
        return "ЄДРПОУ має містити 8 цифр, ІПН - 10 цифр"

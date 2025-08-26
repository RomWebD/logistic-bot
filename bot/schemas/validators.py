"""
Pydantic валідатори
"""

from pydantic import field_validator
from bot.utils.phone import PhoneService


class PhoneValidatorMixin:
    """Mixin для Pydantic моделей з телефонами"""

    @field_validator("phone")
    @classmethod
    def validate_and_normalize_phone(cls, v: str, info) -> str:
        """
        Валідація та нормалізація телефону
        info.data містить інші поля моделі
        """
        if not v:
            raise ValueError("Телефон обов'язковий")

        # Можна взяти країну з контексту
        country = info.data.get("country_code", "UA")

        is_valid, formatted, error = PhoneService.parse_and_validate(v, country)

        if not is_valid:
            raise ValueError(error)

        return formatted  # Повертаємо E164 формат

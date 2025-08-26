"""
📱 МІЖНАРОДНА ВАЛІДАЦІЯ ТЕЛЕФОНІВ
Використовуємо Google libphonenumber
"""

import phonenumbers
# from phonenumbers import geocoder, carrier, timezone
from typing import Optional, Dict, Any, Tuple
import re
from functools import lru_cache


class PhoneService:
    """
    Сервіс для роботи з телефонними номерами
    Singleton pattern через класовий підхід
    """

    # Кешуємо результати для оптимізації
    @classmethod
    @lru_cache(maxsize=1000)
    def parse_and_validate(
        cls, phone: str, default_country: str = "UA"
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Парсинг та валідація номера

        Returns:
            (is_valid, formatted_e164, error_message)
        """
        try:
            # Базове очищення
            cleaned = cls._clean_number(phone)

            # Парсинг
            parsed = None

            # Спроба парсити як міжнародний
            if cleaned.startswith("+"):
                try:
                    parsed = phonenumbers.parse(cleaned, None)
                except phonenumbers.NumberParseException:
                    print(f"{str(phonenumbers.NumberParseException)}")

            # Якщо не вдалось - використовуємо країну за замовчуванням
            if not parsed:
                parsed = phonenumbers.parse(cleaned, default_country)

            # Валідація
            if not phonenumbers.is_valid_number(parsed):
                return False, None, "Невалідний номер телефону"

            # Форматування в E164
            formatted = phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.E164
            )

            return True, formatted, None

        except phonenumbers.NumberParseException as e:
            error_map = {
                phonenumbers.NumberParseException.INVALID_COUNTRY_CODE: "Невірний код країни",
                phonenumbers.NumberParseException.NOT_A_NUMBER: "Це не телефонний номер",
                phonenumbers.NumberParseException.TOO_SHORT_NSN: "Номер занадто короткий",
                phonenumbers.NumberParseException.TOO_LONG: "Номер занадто довгий",
            }
            return False, None, error_map.get(e.error_type, "Невірний формат")
        except Exception:
            return False, None, "Помилка парсингу номера"

    @staticmethod
    def _clean_number(phone: str) -> str:
        """Очищення номера від зайвого"""
        # Замінюємо 00 на + на початку
        if phone.strip().startswith("00"):
            phone = "+" + phone[2:]

        # Зберігаємо + на початку
        has_plus = phone.strip().startswith("+")

        # Видаляємо все крім цифр
        digits = re.sub(r"\D", "", phone)

        return ("+" + digits) if has_plus else digits

    @classmethod
    def format_for_display(cls, phone: str, style: str = "international") -> str:
        """
        Форматування для відображення

        Args:
            style: "international" | "national" | "e164"
        """
        try:
            parsed = phonenumbers.parse(phone, None)

            if style == "international":
                return phonenumbers.format_number(
                    parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
                )
            elif style == "national":
                return phonenumbers.format_number(
                    parsed, phonenumbers.PhoneNumberFormat.NATIONAL
                )
            else:  # e164
                return phonenumbers.format_number(
                    parsed, phonenumbers.PhoneNumberFormat.E164
                )
        except Exception as err:
            print(f"err:{str(err)}")
            pass

    @classmethod
    def get_info(cls, phone: str) -> Dict[str, Any]:
        """Отримати повну інформацію про номер"""
        try:
            parsed = phonenumbers.parse(phone, None)

            if not phonenumbers.is_valid_number(parsed):
                return {"valid": False}

            # Тип номера
            number_type = phonenumbers.number_type(parsed)
            type_map = {
                phonenumbers.PhoneNumberType.MOBILE: "mobile",
                phonenumbers.PhoneNumberType.FIXED_LINE: "fixed",
                phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "fixed_or_mobile",
                phonenumbers.PhoneNumberType.VOIP: "voip",
            }

            info = {
                "valid": True,
                "country_code": phonenumbers.region_code_for_number(parsed),
                "country": geocoder.country_name_for_number(parsed, "en"),
                "type": type_map.get(number_type, "unknown"),
                "formatted": {
                    "e164": phonenumbers.format_number(
                        parsed, phonenumbers.PhoneNumberFormat.E164
                    ),
                    "international": phonenumbers.format_number(
                        parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
                    ),
                    "national": phonenumbers.format_number(
                        parsed, phonenumbers.PhoneNumberFormat.NATIONAL
                    ),
                },
            }

            # Оператор (не для всіх країн)
            try:
                operator = carrier.name_for_number(parsed, "en")
                if operator:
                    info["carrier"] = operator
            except Exception as err:
                print(f"err:{str(err)}")
                pass

            # Часові зони
            try:
                zones = timezone.time_zones_for_number(parsed)
                if zones:
                    info["timezones"] = list(zones)
            except Exception as err:
                print(f"err:{str(err)}")
                pass

            return info

        except Exception as err:
            print(f"err:{str(err)}")
            return {"valid": False}

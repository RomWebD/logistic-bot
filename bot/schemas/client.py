# bot/schemas/client.py
from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import Optional, Tuple
import re
from urllib.parse import urlsplit

# ---------- ХЕЛПЕРИ ДЛЯ КРОКІВ (повертають (normalized, error)) ----------


def validate_full_name_input(text: str) -> tuple[Optional[str], Optional[str]]:
    s = (text or "").strip()
    if len(s) < 2:
        return None, "ПІБ занадто коротке (мінімум 2 символи)."
    return s, None


_PHONE_ALLOWED = re.compile(r"^\+?[0-9\s\-\(\)]+$")


def validate_phone_input(text: str) -> tuple[Optional[str], Optional[str]]:
    s = (text or "").strip()
    if not _PHONE_ALLOWED.match(s):
        return (
            None,
            "Невірний формат телефону. Дозволені тільки +, цифри, пробіли, дужки, дефіси.",
        )
    digits = re.sub(r"\D", "", s)
    if len(digits) < 10 or len(digits) > 15:
        return None, "Телефон має містити від 10 до 15 цифр."
    # простенька нормалізація UA: 0XXXXXXXXX -> +380XXXXXXXXX
    if s.startswith("0") and len(digits) == 10:
        return "+380" + digits[1:], None
    # якщо вже з плюсом — лишаємо +<digits>
    if s.startswith("+"):
        return "+" + digits, None
    return digits, None


_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email_input(text: str) -> tuple[Optional[str], Optional[str]]:
    s = (text or "").strip()
    if not _EMAIL_REGEX.match(s):
        return None, "Некоректний email. Приклад: name@example.com"
    return s, None


def validate_company_name_input(text: str) -> tuple[Optional[str], Optional[str]]:
    s = (text or "").strip()
    if len(s) < 2:
        return None, "Назва компанії занадто коротка (мінімум 2 символи)."
    return s, None


def validate_tax_id_input(text: str) -> tuple[Optional[str], Optional[str]]:
    # Для України: ЄДРПОУ — 8 цифр, ІПН (фіз. особа) — 10 цифр. Дозволимо 8 або 10.
    digits = re.sub(r"\D", "", (text or ""))
    if len(digits) not in (8, 10):
        return None, "Введіть 8 (ЄДРПОУ) або 10 (ІПН) цифр без пробілів."
    return digits, None


def validate_website_input(text: str) -> tuple[Optional[str], Optional[str]]:
    s = (text or "").strip()
    if s == "-" or s == "":
        return None, None
    try:
        parts = urlsplit(s)
        if parts.scheme not in ("http", "https") or not parts.netloc:
            return None, "Некоректний URL. Приклад: https://example.com"
        return s, None
    except Exception:
        return None, "Некоректний URL. Приклад: https://example.com"


# ---------- Pydantic модель для фінального сейву ----------


class ClientRegistrationData(BaseModel):
    telegram_id: int = Field(..., ge=1)
    full_name: str = Field(..., min_length=2, max_length=100)
    company_name: str = Field(..., min_length=2, max_length=150)
    tax_id: str = Field(..., min_length=8, max_length=10)
    phone: str = Field(..., min_length=10, max_length=16)
    email: EmailStr
    address: Optional[str] = Field(None, max_length=255)
    website: Optional[HttpUrl] = None

    model_config = dict(str_strip_whitespace=True)

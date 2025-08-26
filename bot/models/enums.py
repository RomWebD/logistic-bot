"""
📚 ВСІ ENUMS В ОДНОМУ МІСЦІ
Enum - це спосіб обмежити можливі значення поля
"""

from enum import Enum


class UserRole(str, Enum):
    """Ролі користувачів в системі"""

    CLIENT = "client"
    CARRIER = "carrier"
    ADMIN = "admin"
    SUPPORT = "support"


class ShipmentStatus(str, Enum):
    """Статуси заявки на перевезення"""

    DRAFT = "draft"  # Чернетка
    PUBLISHED = "published"  # Опублікована
    NEGOTIATING = "negotiating"  # Йдуть переговори
    ACCEPTED = "accepted"  # Прийнята перевізником
    CONFIRMED = "confirmed"  # Підтверджена клієнтом
    IN_TRANSIT = "in_transit"  # В дорозі
    DELIVERED = "delivered"  # Доставлено
    CANCELLED = "cancelled"  # Скасована
    DISPUTED = "disputed"  # Спірна


class CargoType(str, Enum):
    """Типи вантажу"""

    GENERAL = "general"  # Загальний
    FRAGILE = "fragile"  # Крихкий
    LIQUID = "liquid"  # Рідкий
    BULK = "bulk"  # Насипний
    PERISHABLE = "perishable"  # Швидкопсувний
    DANGEROUS = "dangerous"  # Небезпечний
    OVERSIZED = "oversized"  # Негабаритний
    VALUABLE = "valuable"  # Цінний
    LIVESTOCK = "livestock"  # Живність
    OTHER = "other"  # Інше


class VehicleType(str, Enum):
    """Типи транспортних засобів"""

    # Вантажівки
    TRUCK = "truck"  # Звичайна вантажівка
    TRUCK_WITH_TRAILER = "truck_trailer"  # З причепом
    SEMI_TRUCK = "semi_truck"  # Фура/тягач

    # Фургони
    VAN_SMALL = "van_small"  # Малий фургон (до 1.5т)
    VAN_MEDIUM = "van_medium"  # Середній фургон (1.5-3т)
    VAN_LARGE = "van_large"  # Великий фургон (3-5т)

    # Спеціалізовані
    REFRIGERATOR = "refrigerator"  # Рефрижератор
    TANKER = "tanker"  # Цистерна
    FLATBED = "flatbed"  # Платформа
    DUMP_TRUCK = "dump_truck"  # Самоскид
    CRANE_TRUCK = "crane_truck"  # Кран
    TOW_TRUCK = "tow_truck"  # Евакуатор

    # Малі
    PICKUP = "pickup"  # Пікап
    MINIBUS = "minibus"  # Мікроавтобус


class LoadingType(str, Enum):
    """Типи завантаження/розвантаження"""

    MANUAL = "manual"  # Ручне
    FORKLIFT = "forklift"  # Навантажувач
    CRANE = "crane"  # Кран
    RAMP = "ramp"  # Рампа
    TAIL_LIFT = "tail_lift"  # Гідроборт
    SIDE_LOADING = "side"  # Бокове
    TOP_LOADING = "top"  # Верхнє
    PALLET_JACK = "pallet_jack"  # Рокла


class PaymentType(str, Enum):
    """Типи оплати"""

    CASH = "cash"  # Готівка
    CARD = "card"  # Картка
    BANK_TRANSFER = "bank"  # Банківський переказ
    MIXED = "mixed"  # Комбінована
    DEFERRED = "deferred"  # Відстрочка


class VerificationStatus(str, Enum):
    """Статуси верифікації"""

    PENDING = "pending"  # Очікує
    VERIFIED = "verified"  # Верифікований
    REJECTED = "rejected"  # Відхилено
    SUSPENDED = "suspended"  # Призупинено


class OfferStatus(str, Enum):
    """Статуси пропозицій від перевізників"""

    PENDING = "pending"  # Очікує розгляду
    ACCEPTED = "accepted"  # Прийнята
    REJECTED = "rejected"  # Відхилена
    COUNTER = "counter"  # Контрпропозиція
    WITHDRAWN = "withdrawn"  # Відкликана

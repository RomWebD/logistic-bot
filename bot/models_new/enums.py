"""
Всі Enum в одному місці для легкого імпорту
"""
from enum import Enum


class UserRole(str, Enum):
    CLIENT = "client"
    CARRIER = "carrier"
    ADMIN = "admin"


class ShipmentStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    NEGOTIATING = "negotiating"
    ACCEPTED = "accepted"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class TransportType(str, Enum):
    TRUCK = "truck"
    VAN = "van"
    TRAILER = "trailer"
    REFRIGERATOR = "refrigerator"


class LoadingType(str, Enum):
    MANUAL = "manual"
    FORKLIFT = "forklift"
    CRANE = "crane"
    RAMP = "ramp"

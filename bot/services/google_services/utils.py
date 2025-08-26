from bot.models import TransportVehicle, ShipmentRequest


def get_vehicle_headers() -> list[str]:
    return [
        "Тип ТЗ",
        "Номер",
        "Вантажопідйомність",
        "Обʼєм",
        "Спецобладнання",
        "ПІБ водія",
        "Телефон водія",
    ]


def vehicle_to_row(vehicle: TransportVehicle) -> list[str]:
    return [
        vehicle.vehicle_type,
        vehicle.registration_number,
        vehicle.load_capacity_tons,
        vehicle.body_volume_m3 or "",
        vehicle.special_equipment or "",
        vehicle.driver_fullname or "",
        vehicle.driver_phone or "",
    ]


def get_request_headers() -> list[str]:
    return [
        "ID заявки",
        # "Клієнт (Telegram ID)",
        "Місто відправлення",
        "Місто призначення",
        "Дата подачі",
        "Введений текст дати",
        "Тип вантажу",
        "Обʼєм",
        "Вага",
        "Завантаження",
        "Вивантаження",
        "Ціна",
        "Опис",
        "Створено",
    ]


def request_to_row(req: ShipmentRequest) -> list[str]:
    return [
        str(req.id),
        # str(req.client_telegram_id),
        req.from_city,
        req.to_city,
        req.date.strftime("%Y-%m-%d %H:%M") if req.date else "",
        req.date_text or "",
        req.cargo_type or "",
        str(req.volume or ""),
        str(req.weight or ""),
        req.loading or "",
        req.unloading or "",
        str(req.price or ""),
        req.description or "",
        req.created_at.strftime("%Y-%m-%d %H:%M") if req.created_at else "",
    ]

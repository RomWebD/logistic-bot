from bot.models import TransportVehicle

def get_vehicle_headers() -> list[str]:
    return [
        "Тип ТЗ",
        "Номер",
        "Вантажопідйомність",
        "Обʼєм",
        "Спецобладнання",
        "ПІБ водія",
        "Телефон водія"
    ]

def vehicle_to_row(vehicle: TransportVehicle) -> list[str]:
    return [
        vehicle.vehicle_type,
        vehicle.registration_number,
        vehicle.load_capacity_tons,
        vehicle.body_volume_m3 or "",
        vehicle.special_equipment or "",
        vehicle.driver_fullname or "",
        vehicle.driver_phone or ""
    ]
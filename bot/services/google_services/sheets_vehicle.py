# bot/services/google_services/sheets_vehicle.py
from typing import Tuple
from bot.services.google_services.sheets_client import BaseSheetsClient  # якщо є базовий
# або імпортуй те, з чим ти працюєш у RequestSheetManager

class VehicleSheetManager:
    def __init__(self):
        # self.svc_sheets = ...  # так само, як у RequestSheetManager
        from bot.services.google_services.sheets_client import SheetsService
        self.svc_sheets = SheetsService()  # приклад

    def ensure_vehicle_sheet_for_carrier(
        self,
        *,
        tg_id: int,
        carrier_name: str,
        carrier_email: str | None,
        google_sheet_id: str | None,
        google_sheet_url: str | None,
    ) -> Tuple[str, str]:
        """
        Повертає (sheet_id, sheet_url). Створює документ, якщо треба.
        Аркуш: "Автопарк"
        """
        title = f"Автопарк • {carrier_name}"
        sheet_id, sheet_url = self.svc_sheets.ensure_doc_with_sheet(
            google_sheet_id, google_sheet_url, wanted_title=title, sheet_name="Автопарк",
            header=[
                "Тип", "Номер", "Вантажопідй., т", "Обʼєм, м³", "Завантаження",
                "Водій", "Телефон", "Активний"
            ]
        )
        return sheet_id, sheet_url

    def put_row(self, sheet_id: str, sheet_name: str, row: list[str]):
        self.svc_sheets.put_row(sheet_id, sheet_name, row)

def vehicle_to_row(v) -> list[str]:
    return [
        v.vehicle_type or "",
        v.registration_number or "",
        f"{v.load_capacity_tons:.2f}" if v.load_capacity_tons is not None else "",
        f"{v.body_volume_m3:.2f}" if v.body_volume_m3 is not None else "",
        v.loading_equipment or "",
        v.driver_fullname or "",
        v.driver_phone or "",
        "так" if v.is_active else "ні",
    ]

# google_service/exporters.py
from __future__ import annotations
from typing import List
from .sheets_client import GoogleSheetsClient
from .utils import (
    get_vehicle_headers,
    vehicle_to_row,
    get_request_headers,
    request_to_row,
)
from bot.models import TransportVehicle
from bot.models import Shipment_request


class SheetExporterBase:
    """
    SRP: відповідає тільки за 1 аркуш (sheet) у Spreadsheet.
    """

    SHEET_TITLE: str

    def __init__(self, client: GoogleSheetsClient | None = None):
        self.client = client or GoogleSheetsClient()

    def ensure_tab(self, spreadsheet_id: str, headers: List[str]) -> int:
        sheet_id = self.client.find_sheet_id(spreadsheet_id, self.SHEET_TITLE)
        if sheet_id is None:
            sheet_id = self.client.add_sheet(spreadsheet_id, self.SHEET_TITLE)
            # заголовок
            self.client.put_row(spreadsheet_id, self.SHEET_TITLE, headers)
            # ширини
            self.client.set_column_widths(spreadsheet_id, sheet_id, len(headers))
        return sheet_id

    def append_row(self, spreadsheet_id: str, row: List[str], headers: List[str]):
        self.ensure_tab(spreadsheet_id, headers)
        self.client.put_row(spreadsheet_id, self.SHEET_TITLE, row)


class VehicleSheetExporter(SheetExporterBase):
    SHEET_TITLE = "Автомобілі"

    def append_vehicle(self, spreadsheet_id: str, vehicle: TransportVehicle):
        headers = get_vehicle_headers()
        row = vehicle_to_row(vehicle)
        self.append_row(spreadsheet_id, row, headers)


class RequestSheetExporter(SheetExporterBase):
    SHEET_TITLE = "Заявки"

    def append_request(self, spreadsheet_id: str, req: Shipment_request):
        headers = get_request_headers()
        row = request_to_row(req)
        self.append_row(spreadsheet_id, row, headers)

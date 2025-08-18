# google_service/sheets_client.py
from __future__ import annotations
from typing import List, Tuple, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from bot.models.shipment_request import Shipment_request
from .auth import get_credentials
from .utils import get_request_headers, request_to_row

DEFAULT_COLUMN_WIDTH = 150

REQUEST_SHEET_TITLE = "Заявки"

REQUEST_SHEET_TITLE = "Заявки"
DEFAULT_COLUMN_WIDTH = 150


class RequestSheetManager:
    def __init__(self):
        self.client = GoogleSheetsClient()

    def create_request_sheet(
        self, client_name: str, client_email: str
    ) -> Tuple[str, str]:
        """Створює новий Google Sheet для заявок клієнта"""
        sheet_id, sheet_url = self.client.create_spreadsheet(f"Заявки: {client_name}")

        # даємо доступ клієнту
        self.client.ensure_user_permission(sheet_id, client_email, role="writer")

        # додаємо лист "Заявки"
        sheet_gid = self.client.add_sheet(sheet_id, REQUEST_SHEET_TITLE)

        # ширина колонок
        self.client.set_column_widths(sheet_id, sheet_gid, len(get_request_headers()))

        # заголовки
        self.client.append_values(
            sheet_id, REQUEST_SHEET_TITLE, [get_request_headers()]
        )

        return sheet_id, sheet_url

    def append_request(self, sheet_id: str, request: Shipment_request):
        """Додає заявку в Google Sheet"""
        row = request_to_row(request)
        self.client.put_row(sheet_id, REQUEST_SHEET_TITLE, row)


class GoogleSheetsClient:
    def __init__(self):
        creds = get_credentials()
        self.sheets = build("sheets", "v4", credentials=creds)
        self.drive = build("drive", "v3", credentials=creds)

    # ---------- Drive ----------
    def create_spreadsheet(self, title: str) -> Tuple[str, str]:
        body = {"properties": {"title": title}}
        sheet = self.sheets.spreadsheets().create(body=body).execute()
        return sheet["spreadsheetId"], sheet["spreadsheetUrl"]

    def create_request_sheet(
        self, client_name: str, client_email: str
    ) -> Tuple[str, str]:
        """Створює новий Google Sheet для заявок клієнта"""
        sheet_id, sheet_url = self.client.create_spreadsheet(f"Заявки: {client_name}")

        # даємо доступ клієнту
        self.client.ensure_user_permission(sheet_id, client_email, role="writer")

        # додаємо лист "Заявки"
        sheet_gid = self.client.add_sheet(sheet_id, REQUEST_SHEET_TITLE)

        # ширина колонок
        self.client.set_column_widths(sheet_id, sheet_gid, len(get_request_headers()))

        # заголовки
        self.client.append_values(
            sheet_id, REQUEST_SHEET_TITLE, [get_request_headers()]
        )

        return sheet_id, sheet_url

    def append_request(self, sheet_id: str, request: Shipment_request):
        """Додає заявку в Google Sheet"""
        row = request_to_row(request)
        self.client.put_row(sheet_id, REQUEST_SHEET_TITLE, row)

    def ensure_user_permission(
        self, file_id: str, user_email: str, role: str = "writer"
    ):
        """
        role: 'reader' | 'commenter' | 'writer'
        """
        permission = {"type": "user", "role": role, "emailAddress": user_email}
        # sendNotificationEmail=False — щоб не спамити користувача
        self.drive.permissions().create(
            fileId=file_id, body=permission, sendNotificationEmail=False
        ).execute()

    # ---------- Sheets ----------
    def get_metadata(self, spreadsheet_id: str) -> dict:
        return self.sheets.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()

    def find_sheet_id(self, spreadsheet_id: str, title: str) -> Optional[int]:
        meta = self.get_metadata(spreadsheet_id)
        for s in meta.get("sheets", []):
            if s["properties"]["title"] == title:
                return s["properties"]["sheetId"]
        return None

    def add_sheet(self, spreadsheet_id: str, title: str) -> int:
        resp = (
            self.sheets.spreadsheets()
            .batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": [{"addSheet": {"properties": {"title": title}}}]},
            )
            .execute()
        )
        return resp["replies"][0]["addSheet"]["properties"]["sheetId"]

    def set_column_widths(
        self,
        spreadsheet_id: str,
        sheet_id: int,
        columns: int,
        pixel_size: int = DEFAULT_COLUMN_WIDTH,
    ):
        req = {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": columns,
                },
                "properties": {"pixelSize": pixel_size},
                "fields": "pixelSize",
            }
        }
        self.sheets.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body={"requests": [req]}
        ).execute()

    def append_values(
        self, spreadsheet_id: str, sheet_title: str, values: List[List[str]]
    ):
        self.sheets.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_title}!A1",
            valueInputOption="RAW",
            body={"values": values},
        ).execute()

    def put_row(self, spreadsheet_id: str, sheet_title: str, row: List[str]):
        self.append_values(spreadsheet_id, sheet_title, [row])

# google_service/sheets_client.py
from __future__ import annotations
from typing import List, Tuple, Optional, Dict, Any
from googleapiclient.errors import HttpError

from googleapiclient.discovery import build

from bot.models.shipment_request import Shipment_request
from .auth import get_credentials
from .utils import get_request_headers, request_to_row

DEFAULT_COLUMN_WIDTH = 150
REQUEST_SHEET_TITLE = "Заявки"
TELEGRAM_ID_PROP = "telegram_id"


# -------------------- Low-level Services --------------------


class GoogleSheetsService:
    """Низькорівневий клієнт для Google Sheets API."""

    def __init__(self):
        creds = get_credentials()
        self.sheets = build("sheets", "v4", credentials=creds)

    def create_spreadsheet(
        self, title: str, sheet_title: str = "Заявки"
    ) -> Tuple[str, str]:
        body = {
            "properties": {"title": title},
            "sheets": [{"properties": {"title": sheet_title}}],
        }
        sheet = self.sheets.spreadsheets().create(body=body).execute()
        return sheet["spreadsheetId"], sheet["spreadsheetUrl"]

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


class GoogleDriveService:
    """Низькорівневий клієнт для Google Drive API (права, ревізії, метадані)."""

    def __init__(self):
        creds = get_credentials()
        self.drive = build("drive", "v3", credentials=creds)

    def find_file_by_telegram_id(self, tg_id: int) -> Optional[Dict[str, str]]:
        """
        Шукає файл, де appProperties.telegram_id = tg_id.
        Повертає {id, webViewLink} або None.
        """
        query = f"appProperties has {{ key='{TELEGRAM_ID_PROP}' and value='{tg_id}' }}"
        fields = "files(id, name, webViewLink)"
        resp = self.drive.files().list(q=query, fields=fields, pageSize=1).execute()
        files = resp.get("files", [])
        if not files:
            return None
        return {"id": files[0]["id"], "url": files[0]["webViewLink"]}

    def ensure_user_permission(
        self, file_id: str, user_email: str, role: str = "writer"
    ):
        """
        role: 'reader' | 'commenter' | 'writer'
        """
        permission = {"type": "user", "role": role, "emailAddress": user_email}
        self.drive.permissions().create(
            fileId=file_id, body=permission, sendNotificationEmail=False
        ).execute()

    def set_app_properties(self, file_id: str, props: Dict[str, str]) -> None:
        """
        Встановлює appProperties для файлу.
        Використовується для збереження зв’язку file <-> telegram_id.
        """
        body = {"appProperties": props}
        self.drive.files().update(fileId=file_id, body=body, fields="id").execute()

    def get_latest_revision_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Повертає інформацію про останню ревізію:
        { 'id': str, 'modifiedTime': str (ISO), 'user': { displayName, emailAddress } }
        """
        fields = (
            "revisions(id, modifiedTime, lastModifyingUser(displayName,emailAddress))"
        )
        resp = self.drive.revisions().list(fileId=file_id, fields=fields).execute()
        revs = resp.get("revisions", [])
        if not revs:
            return None
        latest = max(revs, key=lambda r: r.get("modifiedTime", ""))
        return {
            "id": latest.get("id"),
            "modifiedTime": latest.get("modifiedTime"),
            "user": (latest.get("lastModifyingUser") or {}),
        }


# -------------------- Orchestrator / Manager --------------------


class RequestSheetManager:
    """
    Вищий рівень: створення/налаштування таблиці “Заявки”,
    дозвіли, запис рядків, ревізії.
    """

    def __init__(self):
        self.svc_sheets = GoogleSheetsService()
        self.svc_drive = GoogleDriveService()

    def get_latest_revision_info(self, sheet_id: str) -> Optional[Dict[str, Any]]:
        """Повертає дані про останню ревізію (id/час/користувач)."""
        return self.svc_drive.get_latest_revision_info(sheet_id)

    def file_exists(self, file_id: str) -> bool:
        """Перевіряє, чи існує файл у Google Drive."""
        try:
            self.svc_drive.drive.files().get(fileId=file_id, fields="id").execute()
            return True
        except HttpError as e:
            if e.resp.status == 404:
                return False
            raise

    def create_request_sheet_for_client(
        self,
        tg_id: int,
        client_name: str,
        client_email: str | None,
    ) -> Tuple[str, str]:
        """
        Створює новий Google Sheet для клієнта:
        - створює файл
        - тегує його appProperties.telegram_id
        - додає лист "Заявки"
        - виставляє ширину колонок
        - записує заголовки
        - надає права клієнту (writer)
        """
        # 1) створюємо файл
        sheet_id, sheet_url = self.svc_sheets.create_spreadsheet(
            f"Заявки: {client_name}", sheet_title="Заявки"
        )

        # 2) тегуємо file -> telegram_id
        self.svc_drive.set_app_properties(sheet_id, {TELEGRAM_ID_PROP: str(tg_id)})

        # 3) права
        if client_email:
            self.svc_drive.ensure_user_permission(sheet_id, client_email, role="writer")

        # 4) додаємо лист "Заявки"
        sheet_gid = self.svc_sheets.find_sheet_id(sheet_id, "Заявки")

        # 5) колонки
        self.svc_sheets.set_column_widths(
            sheet_id, sheet_gid, len(get_request_headers())
        )

        # 6) заголовки
        self.svc_sheets.append_values(
            sheet_id, REQUEST_SHEET_TITLE, [get_request_headers()]
        )

        return sheet_id, sheet_url

    def ensure_request_sheet_for_client(
        self,
        tg_id: int,
        client_full_name: str,
        client_email: Optional[str],
        google_sheet_id: Optional[str],
        google_sheet_url: Optional[str],
    ) -> Tuple[str, str]:
        """
        Повертає існуючу або нову таблицю.
        - Якщо є sheet_id/url в БД → перевіряємо, чи файл реально існує.
            - Якщо існує → повертаємо.
            - Якщо видалений → створюємо новий і його треба перезаписати в БД.
        - Якщо в БД нема → шукаємо в Drive по appProperties.
        - Якщо нема і там → створюємо новий.
        """
        # 1) Якщо в БД є sheet_id
        if google_sheet_id and google_sheet_url:
            if self.file_exists(google_sheet_id):
                return google_sheet_id, google_sheet_url
            # ⛔ файл видалено → створюємо новий
            return self.create_request_sheet_for_client(
                tg_id, client_full_name, client_email
            )

        # 2) шукаємо по appProperties
        found = self.svc_drive.find_file_by_telegram_id(tg_id)
        if found and self.file_exists(found["id"]):
            return found["id"], found["url"]

        # 3) створюємо новий
        return self.create_request_sheet_for_client(
            tg_id, client_full_name, client_email
        )

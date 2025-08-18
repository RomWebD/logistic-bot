# google_service/spreadsheet_manager.py
from __future__ import annotations
from typing import Tuple
from .sheets_client import GoogleSheetsClient

class SpreadsheetManager:
    """
    Відповідає тільки за Spreadsheet (файл):
    - створити, якщо нема
    - видати доступ користувачу за email
    - повернути (spreadsheetId, spreadsheetUrl)
    Зберігати/кешувати sheet_id/url варто у вашій БД профілю/компанії.
    """
    def __init__(self, client: GoogleSheetsClient | None = None):
        self.client = client or GoogleSheetsClient()

    def ensure_company_spreadsheet(self, company_title: str, user_email: str) -> Tuple[str, str]:
        # Створюємо завжди новий або (краще) спершу шукаємо в БД, чи вже є.
        # Тут — простий варіант: створюємо новий файл.
        spreadsheet_id, spreadsheet_url = self.client.create_spreadsheet(f"Компанія: {company_title}")
        self.client.ensure_user_permission(spreadsheet_id, user_email, role="writer")
        return spreadsheet_id, spreadsheet_url

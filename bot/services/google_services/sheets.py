# google_service/sheets.py
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .auth import get_credentials
from .utils import get_vehicle_headers, vehicle_to_row
from bot.models import TransportVehicle

SHEET_TITLE = "Автомобілі"
DEFAULT_COLUMN_WIDTH = 150  # Ширина в пікселях (налаштовуй за смаком)
CLIENT_SHEET_TITLE = "Заявки"


def get_sheets_service():
    creds = get_credentials()
    return build("sheets", "v4", credentials=creds)


def get_drive_service():
    creds = get_credentials()
    return build("drive", "v3", credentials=creds)


def create_sheet_if_not_exists(company_name: str, user_email: str) -> tuple[str, str]:
    """Створює Google Sheet, якщо він ще не створений. Повертає (sheet_id, sheet_url)"""
    sheets_service = get_sheets_service()
    drive_service = get_drive_service()
    HEADER_ROW = get_vehicle_headers()
    # Створення
    body = {
        "properties": {"title": f"Компанія: {company_name}"},
        "sheets": [{"properties": {"title": SHEET_TITLE}}],
    }
    try:
        sheet = sheets_service.spreadsheets().create(body=body).execute()
        sheet_id = sheet["spreadsheetId"]
        sheet_url = sheet["spreadsheetUrl"]

        # Доступ для юзера
        permission = {
            "type": "user",
            "role": "writer",  # або "reader", якщо потрібно лише перегляд
            "emailAddress": user_email,
        }
        drive_service.permissions().create(
            fileId=sheet_id,
            body=permission,
            sendNotificationEmail=False,
        ).execute()

        # Додаємо заголовки
        sheets_service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=f"{SHEET_TITLE}!A1",
            valueInputOption="USER_ENTERED",
            body={"values": [HEADER_ROW]},
        ).execute()
        # Отримати ID листа
        sheet_metadata = (
            sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        )
        sheet_gid = next(
            s["properties"]["sheetId"]
            for s in sheet_metadata["sheets"]
            if s["properties"]["title"] == SHEET_TITLE
        )

        # Змінити ширину колонок
        requests = [
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet_gid,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": len(HEADER_ROW),
                    },
                    "properties": {
                        "pixelSize": DEFAULT_COLUMN_WIDTH,
                    },
                    "fields": "pixelSize",
                }
            }
        ]

        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id, body={"requests": requests}
        ).execute()
        return sheet_id, sheet_url

    except HttpError as e:
        raise RuntimeError(f"Помилка створення Google Sheet: {e}")


def append_vehicle_to_sheet(sheet_id: str, vehicle: TransportVehicle):
    """
    Додає запис транспортного засобу в існуючий Google Sheet.
    """
    try:
        sheets_service = get_sheets_service()
        row = vehicle_to_row(vehicle)
        sheets_service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=f"{SHEET_TITLE}!A1",
            valueInputOption="RAW",
            body={"values": [row]},
        ).execute()

    except HttpError as e:
        raise RuntimeError(f"❌ Failed to append vehicle: {e}")

# bot/services/google_sheets_service.py
import gspread
from google.oauth2.service_account import Credentials
from decouple import config

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

CREDENTIALS_PATH = config("GOOGLE_CREDS_PATH")  # 👈 читаємо з .env

credentials = Credentials.from_service_account_file(
    CREDENTIALS_PATH,
    scopes=SCOPES,
)

gc = gspread.authorize(credentials)


def create_company_sheet(company_name: str, user_email: str) -> str:
    """
    Створює новий Google Sheet, додає аркуш `cars`, записує заголовки та дає доступ користувачу.

    :param company_name: Назва компанії
    :param user_email: Email користувача
    :return: Посилання на створений файл
    """
    spreadsheet = gc.create(f"Компанія: {company_name}")
    spreadsheet.share(user_email, perm_type="user", role="writer")

    worksheet = spreadsheet.sheet1
    worksheet.update_title("cars")

    headers = [
        "Тип ТЗ",
        "Марка",
        "Рік",
        "Номер",
        "Вантажопідйомність",
        "Розмір кузова",
        "Спецобладнання",
        "Регіони покриття",
    ]
    worksheet.append_row(headers)

    return spreadsheet.url

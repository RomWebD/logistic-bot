# bot/services/google_sheets_service.py
import gspread
from google.oauth2.service_account import Credentials
from decouple import config
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from typing import List

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
SPREADSHEET_TITLE = "Автомобілі"

CREDENTIALS_PATH = config("GOOGLE_CREDS_PATH")  # 👈 читаємо з .env
# services/google_sheets_service.py


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_TITLE = "Автомобілі"


def get_google_service():
    creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)

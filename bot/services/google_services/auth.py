import os
from google.auth.transport.requests import Request  # 👈 оце потрібний імпорт!
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


from decouple import config

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


CREDENTIALS_PATH = config("GOOGLE_CREDS_PATH")

TOKEN_PATH = "secrets/token.pickle"  # тут збережеться access+refresh токен


def get_credentials():
    creds = None

    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    # 🔥 обов'язково перезаписати токен у файл
                    with open(TOKEN_PATH, "w") as token:
                        token.write(creds.to_json())
                else:
                    raise RefreshError("Invalid or expired credentials")
        except RefreshError:
            print("⚠️ Refresh token протух або відкликаний. Видаляю файл...")
            os.remove(TOKEN_PATH)
            creds = None

    # Якщо нема токену — запускаємо повну авторизацію
    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(port=0)

        # Зберегти для наступного разу
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return creds

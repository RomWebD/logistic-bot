import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from decouple import config

# Скопійовано з Google Cloud API docs
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",  # доступ лише до створених файлів
    "https://www.googleapis.com/auth/spreadsheets",
]
CREDENTIALS_PATH = config("GOOGLE_CREDS_PATH")

TOKEN_PATH = "token.pickle"  # тут збережеться access+refresh токен


def get_credentials():
    if os.path.exists(TOKEN_PATH):
        return Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
    creds = flow.run_local_server(port=0)

    with open(TOKEN_PATH, "w") as token_file:
        token_file.write(creds.to_json())

    return creds

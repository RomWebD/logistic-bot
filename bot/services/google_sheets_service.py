# import gspread
# from google.oauth2.service_account import Credentials
# from decouple import config

# from bot.models.TransportVehicle import TransportVehicle

# # --- Налаштування ---
# SCOPES = [
#     "https://www.googleapis.com/auth/spreadsheets",
#     "https://www.googleapis.com/auth/drive",
# ]
# CREDENTIALS_PATH = config("GOOGLE_CREDS_PATH")

# credentials = Credentials.from_service_account_file(
#     CREDENTIALS_PATH,
#     scopes=SCOPES,
# )
# gc = gspread.authorize(credentials)

# # --- Заголовки таблиці ---
# SHEET_HEADERS = [
#     "Тип ТЗ",
#     "Номер(и) авто",
#     "Вантажопідйомність",
#     "Обʼєм",
#     "Спецобладнання",
#     "ПІБ водія",
#     "Телефон водія",
# ]


# # --- Створення нового Google Sheet для компанії ---
# def create_company_vehicle_sheet(
#     company_name: str, company_email: str
# ) -> tuple[str, str]:
#     """
#     Створює Google Sheet з назвою компанії, додає аркуш "Автомобілі",
#     записує заголовки та надає доступ користувачу за email.

#     :param company_name: Назва компанії
#     :param company_email: Email користувача
#     :return: (sheet_url, sheet_id)
#     """
#     spreadsheet = gc.create(f"Компанія: {company_name}")
#     spreadsheet.share(company_email, perm_type="user", role="reader")

#     worksheet = spreadsheet.sheet1
#     worksheet.update_title("Автомобілі")
#     worksheet.append_row(SHEET_HEADERS)

#     return spreadsheet.url, spreadsheet.id


# # --- Додавання нового авто в існуючий файл ---
# def append_vehicle_to_sheet(sheet_id: str, vehicle: TransportVehicle) -> None:
#     """
#     Додає новий рядок у Google Sheet з даними транспортного засобу.

#     :param sheet_id: ID Google Sheet файлу
#     :param vehicle: Обʼєкт TransportVehicle
#     """
#     spreadsheet = gc.open_by_key(sheet_id)
#     worksheet = spreadsheet.worksheet("Автомобілі")

#     row = [
#         vehicle.vehicle_type,
#         vehicle.registration_number,
#         vehicle.load_capacity_tons,
#         vehicle.body_volume_m3 or "-",
#         vehicle.special_equipment or "-",
#         vehicle.driver_fullname or "-",
#         vehicle.driver_phone or "-",
#     ]

#     worksheet.append_row(row)

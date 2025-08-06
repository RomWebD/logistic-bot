from aiogram.fsm.state import StatesGroup, State

class RegisterCar(StatesGroup):
    car_type = State()
    plate_number = State()
    weight_capacity = State()
    volume = State()
    loading_type = State()
    driver_fullname = State()
    driver_phone = State()


ALL_FIELDS = [
    "car_type",
    "plate_number",
    "weight_capacity",
    "volume",
    "loading_type",
    "driver_fullname",
    "driver_phone",
]


def get_progress_bar(state_data: dict) -> str:
    filled = sum(1 for field in ALL_FIELDS if state_data.get(field))
    percent = int((filled / len(ALL_FIELDS)) * 100)
    blocks = int(percent / 10)
    return f"\n\n📊 Прогрес: [{'■' * blocks}{'□' * (10 - blocks)}] {percent}%"
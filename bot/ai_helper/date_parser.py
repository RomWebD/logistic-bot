from groq import Groq
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def normalize_date_with_groq(input_text: str) -> datetime | None:
    now: datetime = datetime.now()
    prompt = f"""
Сьогодні: {now.strftime("%Y-%m-%d %H:%M")}

Введена дата: "{input_text}"

❗ Перетвори у формат: YYYY-MM-DD HH:MM
❗ Дата не може бути в минулому.
❗ Якщо рік або час не вказані — постав найближчі значення в майбутньому.
Поверни лише результат, без коментарів.
"""

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        stream=False,
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        print(datetime.strptime(raw_output, "%Y-%m-%d %H:%M"))
        return datetime.strptime(raw_output, "%Y-%m-%d %H:%M")
    except ValueError:
        print(f"⛔️ Не вдалося розпарсити дату: {raw_output}")
        return None


test_data = "20 липня до 10:00"
normalize_date_with_groq(test_data)

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

if not BOT_TOKEN:
    raise SystemExit(
        "TELEGRAM_BOT_TOKEN .env faylida ko'rsatilmagan. "
        "Bot ishga tushishi uchun @BotFather dan token oling va .env ga qo'ying."
    )
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
_default_backend = (
    f"http://127.0.0.1:{os.getenv('PORT', '8000')}" if os.getenv("PORT") else "http://127.0.0.1:8000"
)
BACKEND_URL = os.getenv("BACKEND_URL", _default_backend).rstrip("/")

if not BOT_TOKEN:
    raise SystemExit(
        "TELEGRAM_BOT_TOKEN .env faylida ko'rsatilmagan. "
        "Bot ishga tushishi uchun @BotFather dan token oling va .env ga qo'ying."
    )
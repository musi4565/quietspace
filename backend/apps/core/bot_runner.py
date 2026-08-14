"""Telegram botni Django processi ichida ishga tushirish (Render free tier uchun).

Nega thread? Render'ning bepul tarifida "background worker" turi mavjud emas,
shuning uchun bot gunicorn bilan birga, bitta process ichida ishlaydi.
Bot alohida thread va o'z asyncio event loop'ida ishga tushiriladi.

Nega bitta worker? Gunicorn bir nechta worker fork qilsa, har birida bot
polling boshlasa, Telegram "Conflict: terminated by other getUpdates request"
xatosi beradi. Shuning uchun start.sh da gunicorn --workers 1 bilan
ishlatiladi va bot faqat shu bitta worker'da (ready() orqali) bir marta
ishga tushadi.
"""

import logging
import os
import sys
import threading
from pathlib import Path

logger = logging.getLogger(__name__)

BOT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "bot"

_detected = None


def should_start_bot() -> bool:
    """Botni ishga tushirish kerakmi? (runserver / gunicorn bo'lsa)"""
    global _detected
    if _detected is None:
        _detected = _detect()
    return _detected


def _detect() -> bool:
    if os.environ.get("BOT_AUTOSTART") == "0":
        return False
    argv0 = os.path.basename(sys.argv[0] or "").lower()
    args = sys.argv[1:]
    is_gunicorn = argv0.startswith("gunicorn")
    is_runserver = any(arg == "runserver" for arg in args)
    return is_gunicorn or is_runserver


def start_bot() -> None:
    if not should_start_bot():
        return
    if not BOT_DIR.exists():
        logger.warning("Bot papkasi topilmadi: %s", BOT_DIR)
        return
    thread = threading.Thread(target=_run_bot, name="telegram-bot", daemon=True)
    thread.start()
    logger.info("Telegram bot thread ishga tushdi (daemon)")


def _run_bot() -> None:
    try:
        import asyncio

        sys.path.insert(0, str(BOT_DIR.parent))
        from bot import main as bot_main  # noqa: F401

        async def _main():
            await bot_main.main()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_main())
    except SystemExit as exc:
        logger.warning(
            "Bot to'xtatildi (SystemExit %s): TELEGRAM_BOT_TOKEN sozlanmagan bo'lishi mumkin.", exc
        )
    except Exception:
        logger.exception("Telegram bot threadda xatolik yuz berdi")
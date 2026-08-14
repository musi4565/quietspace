"""Env sozlamalarini tekshirish (qiymatlarni ko'rsatmaydi).

Ishlatish: python manage.py check_config
"""

from django.core.management.base import BaseCommand
from django.conf import settings


REQUIRED = ["SECRET_KEY", "DATABASE_NAME", "DATABASE_USER", "DATABASE_PASSWORD"]
AI_KEYS = ["GEMINI_API_KEY", "AI_API_KEY"]
BOT_KEYS = ["TELEGRAM_BOT_TOKEN"]


class Command(BaseCommand):
    help = "Environment variable'larni tekshiradi (qiymatlarni chiqarmaydi)."

    def handle(self, *args, **options):
        import os

        rows = []
        for key in REQUIRED + AI_KEYS + BOT_KEYS:
            value = os.environ.get(key, "")
            status = "SET" if value.strip() else "EMPTY"
            rows.append((key, status))

        self.stdout.write("=== Environment tekshiruvi (qiymatlar ko'rsatilmaydi) ===")
        for key, status in rows:
            color = self.style.SUCCESS if status == "SET" else self.style.ERROR
            self.stdout.write(f"  {key:<28} {color(status)}")

        ai_provider = (
            "gemini" if settings.GEMINI_API_KEY else "openai" if settings.AI_API_KEY else "rule-based"
        )
        self.stdout.write(f"\nFaol AI provider: {ai_provider}")

        if not os.environ.get("TELEGRAM_BOT_TOKEN", "").strip():
            self.stdout.write(self.style.WARNING("Ogohlantirish: TELEGRAM_BOT_TOKEN bo'sh - bot ishga tushmaydi."))
        if not settings.GEMINI_API_KEY and not settings.AI_API_KEY:
            self.stdout.write(self.style.WARNING("Ogohlantirish: AI kaliti yo'q - rule-based parser ishlaydi."))

        self.stdout.write(self.style.SUCCESS("Tekshiruv tugadi."))
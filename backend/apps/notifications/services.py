import logging

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org"


def send_telegram_message(chat_id: str, text: str) -> bool:
    """Telegram Bot API orqali xabar yuboradi. Token bo'lmasa xato yozib False qaytaradi."""
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.warning(
            "TELEGRAM_BOT_TOKEN sozlanmagan - xabar yuborilmadi. "
            "Xabar yuborish uchun .env faylida TELEGRAM_BOT_TOKEN ni o'rnating."
        )
        return False
    try:
        response = httpx.post(
            f"{TELEGRAM_API}/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()
        return bool(result.get("ok"))
    except Exception as exc:
        logger.error("Telegram xabar yuborishda xato: %s", exc)
        return False


def notify_new_approved_place(place) -> int:
    """Yangi APPROVED joy paydo bo'lganda mos subscription'larga xabar yuboradi."""
    from apps.notifications.models import NotificationSubscription

    sent = 0
    subscriptions = NotificationSubscription.objects.filter(is_active=True).select_related("district")
    for sub in subscriptions:
        if sub.matches(place):
            price_text = "Bepul" if place.price_per_hour == 0 else f"{place.price_per_hour:,} so'm".replace(",", " ")
            socket_text = "Bor" if place.socket_count else "Yo'q"
            text = (
                "🔔 Sizga mos yangi joy!\n\n"
                f"🏠 {place.name}\n"
                f"📍 {place.district.name}\n"
                f"🤫 {place.get_noise_level_display()}\n"
                f"📶 Wi-Fi {place.wifi_speed} Mbps\n"
                f"🔌 Rozetka: {socket_text}\n"
                f"💰 {price_text}\n"
                f"🟢 {place.available_slots} ta bo'sh\n\n"
                f"<a href='{settings.FRONTEND_URL}/places/{place.id}'>Batafsil ko'rish</a>"
            )
            if sub.telegram_chat_id and send_telegram_message(sub.telegram_chat_id, text):
                sent += 1
    return sent
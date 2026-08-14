from django.conf import settings
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai.services.matching import MatchingService
from apps.ai.services.parsers import get_parser
from apps.places.serializers import PlaceListSerializer


def _price_str(price):
    if price == 0:
        return "Bepul"
    return f"{price:,} so'm".replace(",", " ")


def build_reply(results, req, source):
    lines = []
    if source == "rule-based":
        lines.append("🤖 Talabingiz tahlil qilindi (kalit so'zlar orqali).")
    else:
        lines.append("🤖 AI talabingizni tahlil qildi.")
    lines.append(f"📋 Talablar: {req}")
    lines.append("")

    if not results:
        lines.append("😔 Hech qanday mos joy topilmadi. Boshqa talab bilan urinib ko'ring.")
        return "\n".join(lines)

    medals = ["🥇", "🥈", "🥉"]
    for idx, item in enumerate(results[:3]):
        place = item["place"]
        percent = item["match_percent"]
        medal = medals[idx] if idx < 3 else f"{idx + 1}."
        lines.append(f"{medal} {place.name}")
        lines.append(f"   {percent}% mos")
        lines.append(f"   🤫 {place.get_noise_level_display()}")
        lines.append(f"   📶 {place.wifi_speed} Mbps")
        lines.append(f"   🔌 {'Bor' if place.socket_count else "Yo'q"}")
        lines.append(f"   💰 {_price_str(place.price_per_hour)}")
        lines.append(f"   📍 {place.district.name}")
        lines.append("")

    if len(results) > 3:
        lines.append(f"Va yana {len(results) - 3} ta mos joy...")
    lines.append("")
    lines.append("Batafsil ko'rish uchun bosing: /place <id>")
    return "\n".join(lines)


class ChatView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        message = (request.data.get("message") or "").strip()
        if not message:
            return Response(
                {"success": False, "message": "message maydoni bo'sh bo'lishi mumkin emas"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        parser = get_parser()
        req = parser.parse(message)

        results = MatchingService.match(req, limit=10)

        parser_class = parser.__class__.__name__
        if parser_class == "GeminiParser":
            source = "gemini"
        elif parser_class == "OpenAICompatParser":
            source = "ai"
        else:
            source = "rule-based"

        serialized = []
        for item in results:
            data = PlaceListSerializer(item["place"], context={"request": request}).data
            serialized.append({"place": data, "match_percent": item["match_percent"]})

        reply = build_reply(results, req, source)

        return Response(
            {
                "success": True,
                "message": reply,
                "requirements": req.to_dict(),
                "source": source,
                "results": serialized,
            }
        )


class AIStatusView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        active_key = settings.GEMINI_API_KEY or settings.AI_API_KEY
        active_provider = (
            "gemini" if settings.GEMINI_API_KEY else settings.AI_PROVIDER if settings.AI_API_KEY else None
        )
        active_model = (
            settings.GEMINI_MODEL if settings.GEMINI_API_KEY else settings.AI_MODEL if settings.AI_API_KEY else None
        )
        return Response(
            {
                "success": True,
                "ai_configured": bool(active_key),
                "provider": active_provider,
                "model": active_model,
                "gemini_configured": bool(settings.GEMINI_API_KEY),
                "openai_configured": bool(settings.AI_API_KEY),
                "message": (
                    f"{active_provider} modeli ({active_model}) ishga tushdi."
                    if active_key
                    else "AI API kaliti sozlanmagan - kalit so'z (rule-based) parser ishlaydi. "
                    "Ishlash uchun .env faylida AI_API_KEY yoki GEMINI_API_KEY ni o'rnating."
                ),
            }
        )
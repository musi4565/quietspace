from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.telegram.models import TelegramLinkCode, TelegramProfile
from apps.telegram.serializers import LinkConfirmSerializer, TelegramProfileSerializer


class LinkRequestView(APIView):
    """Foydalanuvchi bog'lash kodini so'raydi (saytda login bo'lganda)."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        link = TelegramLinkCode.create_for(request.user)
        return Response(
            {
                "success": True,
                "message": "Kod yaratildi. Botda /link <kod> buyrug'ini yuboring.",
                "code": link.code,
                "link_url": link.link_url(),
                "expires_at": link.expires_at,
            },
            status=status.HTTP_201_CREATED,
        )


class LinkConfirmView(APIView):
    """Bot backendga kelgan kodni tasdiqlaydi va chat_id ni user bilan bog'laydi."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LinkConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["code"]
        chat_id = serializer.validated_data["chat_id"]
        username = serializer.validated_data.get("username", "")

        try:
            link = TelegramLinkCode.objects.get(code=code)
        except TelegramLinkCode.DoesNotExist:
            return Response(
                {"success": False, "message": "Kod topilmadi"}, status=status.HTTP_404_NOT_FOUND
            )

        if not link.is_valid():
            return Response(
                {"success": False, "message": "Kod muddati tugagan yoki ishlatilgan"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if link.telegram_chat_id and link.telegram_chat_id != chat_id:
            return Response(
                {"success": False, "message": "Kod boshqa chatda ishlatilgan"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        link.is_used = True
        link.telegram_chat_id = chat_id
        link.save(update_fields=["is_used", "telegram_chat_id"])

        profile, created = TelegramProfile.objects.update_or_create(
            chat_id=chat_id,
            defaults={"user": link.user, "username": username},
        )
        TelegramProfile.objects.filter(user=link.user).exclude(chat_id=chat_id).delete()

        return Response(
            {
                "success": True,
                "message": "Bog'lanish muvaffaqiyatli",
                "user_email": link.user.email,
                "profile": TelegramProfileSerializer(profile).data,
            }
        )


class MyTelegramProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = TelegramProfile.objects.filter(user=request.user).first()
        return Response(
            {
                "success": True,
                "linked": bool(profile),
                "profile": TelegramProfileSerializer(profile).data if profile else None,
            }
        )

    def delete(self, request):
        deleted, _ = TelegramProfile.objects.filter(user=request.user).delete()
        if not deleted:
            return Response({"success": False, "message": "Bog'lanish topilmadi"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"success": True, "message": "Bog'lanish bekor qilindi"})


class BotFavoritesView(APIView):
    """Bot uchun: bog'langan chat_id ning sevimli joylari (demo)."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        chat_id = request.query_params.get("chat_id", "").strip()
        if not chat_id:
            return Response({"success": False, "message": "chat_id kerak"}, status=status.HTTP_400_BAD_REQUEST)
        profile = TelegramProfile.objects.filter(chat_id=str(chat_id)).first()
        if not profile:
            return Response(
                {"success": False, "message": "Hisob Telegram bilan bog'lanmagan. Saytda bog'lang yoki /link <kod> qiling."}
            )
        from apps.favorites.models import Favorite
        from apps.places.models import PlaceStatus
        from apps.places.serializers import PlaceListSerializer

        favs = (
            Favorite.objects.filter(user=profile.user, place__status=PlaceStatus.APPROVED)
            .select_related("place", "place__district")
            .prefetch_related("place__images")
        )
        places = [f.place for f in favs]
        return Response(
            {
                "success": True,
                "user_email": profile.user.email,
                "count": len(places),
                "places": PlaceListSerializer(places, many=True, context={"request": request}).data,
            }
        )


class BotNotificationsToggleView(APIView):
    """Bot uchun: bildirishnomalarni yoqish/o'chirish."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        chat_id = request.data.get("chat_id", "").strip()
        if not chat_id:
            return Response({"success": False, "message": "chat_id kerak"}, status=status.HTTP_400_BAD_REQUEST)
        profile = TelegramProfile.objects.filter(chat_id=str(chat_id)).first()
        if not profile:
            return Response(
                {"success": False, "message": "Hisob Telegram bilan bog'lanmagan. /link <kod> buyrug'ini ishlating."}
            )
        profile.notifications_enabled = not profile.notifications_enabled
        profile.save(update_fields=["notifications_enabled"])
        return Response(
            {
                "success": True,
                "notifications_enabled": profile.notifications_enabled,
                "message": (
                    "🔔 Bildirishnomalar yoqildi"
                    if profile.notifications_enabled
                    else "🔕 Bildirishnomalar o'chirildi"
                ),
            }
        )
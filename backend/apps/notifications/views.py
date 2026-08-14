from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.models import NotificationSubscription
from apps.notifications.serializers import NotificationSubscriptionSerializer, TelegramSubscriptionSerializer
from apps.places.models import District


class SubscriptionListView(generics.ListAPIView):
    serializer_class = NotificationSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NotificationSubscription.objects.filter(user=self.request.user).select_related("district")


class SubscriptionCreateView(generics.CreateAPIView):
    serializer_class = NotificationSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SubscriptionDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            sub = NotificationSubscription.objects.get(pk=pk, user=request.user)
        except NotificationSubscription.DoesNotExist:
            return Response({"success": False, "message": "Obuna topilmadi"}, status=status.HTTP_404_NOT_FOUND)
        sub.delete()
        return Response({"success": True, "message": "Obuna o'chirildi"})


class TelegramSubscriptionView(APIView):
    """Bot orqali subscription yaratish. chat_id ichida keladi."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        chat_id = request.data.get("telegram_chat_id")
        if not chat_id:
            return Response(
                {"success": False, "message": "telegram_chat_id kerak"}, status=status.HTTP_400_BAD_REQUEST
            )
        data = dict(request.data)
        data.pop("telegram_chat_id", None)
        district = data.get("district")
        if district:
            dist = District.objects.filter(slug=district).first() or District.objects.filter(name=district).first()
            data["district"] = dist.id if dist else None

        serializer = TelegramSubscriptionSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(telegram_chat_id=chat_id)
        return Response({"success": True, "message": "Obuna yaratildi", "subscription": serializer.data}, status=status.HTTP_201_CREATED)
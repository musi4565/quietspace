from rest_framework import serializers

from apps.notifications.models import NotificationSubscription
from apps.places.models import District


class NotificationSubscriptionSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source="district.name", read_only=True)
    district = serializers.PrimaryKeyRelatedField(queryset=District.objects.all(), required=False, allow_null=True)

    class Meta:
        model = NotificationSubscription
        fields = [
            "id", "district", "district_name", "max_price", "noise_level",
            "wifi_min", "sockets_required", "is_active", "created_at",
        ]
        read_only_fields = ["id", "district_name", "created_at"]

    def validate_noise_level(self, value):
        if value and value not in ("VERY_QUIET", "QUIET", "AVERAGE", "NOISY"):
            raise serializers.ValidationError("noise_level noto'g'ri")
        return value


class TelegramSubscriptionSerializer(serializers.ModelSerializer):
    """Bot orqali yaratiladigan subscription (chat_id bilan)."""

    class Meta:
        model = NotificationSubscription
        fields = [
            "id", "district", "max_price", "noise_level", "wifi_min",
            "sockets_required", "is_active", "created_at",
        ]
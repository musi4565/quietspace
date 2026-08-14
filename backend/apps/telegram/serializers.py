from rest_framework import serializers

from apps.telegram.models import TelegramLinkCode, TelegramProfile


class LinkRequestSerializer(serializers.Serializer):
    pass


class LinkConfirmSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=64)
    chat_id = serializers.CharField(max_length=100)
    username = serializers.CharField(max_length=100, required=False, allow_blank=True)


class TelegramProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramProfile
        fields = ["id", "chat_id", "username", "notifications_enabled", "linked_at"]
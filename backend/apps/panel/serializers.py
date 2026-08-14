from rest_framework import serializers

from apps.accounts.models import User
from apps.accounts.serializers import UserSerializer


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["role", "is_active"]
        read_only_fields = ["email", "full_name"]


class AdminUserListSerializer(UserSerializer):
    place_count = serializers.IntegerField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ["place_count", "is_active"]
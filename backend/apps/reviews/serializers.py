from django.db.models import Avg, Count
from rest_framework import serializers

from apps.reviews.models import Review
from apps.reviews.validators import validate_feedback


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "place", "rating", "text", "noise_feedback", "wifi_feedback", "created_at"]
        read_only_fields = ["id", "place", "created_at"]

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating 1 dan 5 gacha bo'lishi kerak")
        return value

    def validate_noise_feedback(self, value):
        return validate_feedback(value, ("VERY_QUIET", "AVERAGE", "NOISY"), "noise_feedback")

    def validate_wifi_feedback(self, value):
        return validate_feedback(value, ("EXCELLENT", "GOOD", "AVERAGE", "POOR"), "wifi_feedback")

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    place_name = serializers.CharField(source="place.name", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id", "user", "user_name", "place", "place_name", "rating",
            "text", "noise_feedback", "wifi_feedback", "created_at",
        ]
        read_only_fields = ["id", "user", "user_name", "place_name", "created_at"]
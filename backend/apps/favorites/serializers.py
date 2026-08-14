from django.db.models import Avg
from rest_framework import serializers

from apps.favorites.models import Favorite
from apps.places.models import Place
from apps.places.serializers import PlaceListSerializer


class FavoriteCreateSerializer(serializers.ModelSerializer):
    place = serializers.PrimaryKeyRelatedField(queryset=Place.objects.filter(status="APPROVED"))

    class Meta:
        model = Favorite
        fields = ["id", "place", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        user = self.context["request"].user
        place = attrs["place"]
        if Favorite.objects.filter(user=user, place=place).exists():
            raise serializers.ValidationError({"place": "Bu joy allaqachon sevimlilarda"})
        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class FavoritePlaceSerializer(serializers.ModelSerializer):
    place = PlaceListSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ["id", "place", "created_at"]


class FavoritePlaceListSerializer(PlaceListSerializer):
    avg_rating = serializers.SerializerMethodField()

    class Meta(PlaceListSerializer.Meta):
        fields = PlaceListSerializer.Meta.fields + ["avg_rating"]
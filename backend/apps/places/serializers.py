from django.db.models import Avg, Count
from rest_framework import serializers

from apps.places.models import Availability, District, Place, PlaceImage


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ["id", "name", "slug"]


class PlaceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceImage
        fields = ["id", "image", "is_primary"]
        read_only_fields = ["id"]


class PlaceListSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source="district.name", read_only=True)
    image = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()
    noise_display = serializers.CharField(source="get_noise_level_display", read_only=True)
    distance_km = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = [
            "id", "name", "district_name", "address", "price_per_hour", "wifi_speed",
            "socket_count", "noise_level", "noise_display", "capacity", "available_slots",
            "avg_rating", "image", "latitude", "longitude", "status", "distance_km",
        ]

    def get_distance_km(self, obj):
        value = getattr(obj, "distance_km", None)
        if value is None:
            return None
        return round(float(value), 1)

    def get_image(self, obj):
        img = obj.images.filter(is_primary=True).first() or obj.images.first()
        if img:
            return img.image.url
        return None

    def get_avg_rating(self, obj):
        if hasattr(obj, "avg_rating"):
            return round(obj.avg_rating, 1) if obj.avg_rating else None
        return None


class PlaceDetailSerializer(serializers.ModelSerializer):
    district = DistrictSerializer(read_only=True)
    district_id = serializers.PrimaryKeyRelatedField(
        queryset=District.objects.all(), source="district", write_only=True
    )
    images = PlaceImageSerializer(many=True, read_only=True)
    images_data = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False, allow_empty=True
    )
    avg_rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    noise_display = serializers.CharField(source="get_noise_level_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    owner_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Place
        fields = [
            "id", "name", "description", "district", "district_id", "address",
            "latitude", "longitude", "price_per_hour", "wifi_speed", "socket_count",
            "noise_level", "noise_display", "capacity", "available_slots",
            "open_time", "close_time", "status", "status_display", "is_featured",
            "avg_rating", "rating_count", "images", "images_data", "owner_id",
            "created_at", "updated_at",
        ]
        read_only_fields = ["status", "is_featured", "owner_id", "created_at", "updated_at"]

    def get_avg_rating(self, obj):
        if hasattr(obj, "avg_rating"):
            return round(obj.avg_rating, 1) if obj.avg_rating else None
        return None

    def get_rating_count(self, obj):
        if hasattr(obj, "rating_count"):
            return obj.rating_count or 0
        return 0

    def validate_images_data(self, value):
        for image in value:
            if image.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Rasm hajmi 5 MB dan oshmasligi kerak")
            if not image.content_type.startswith("image/"):
                raise serializers.ValidationError("Faqat rasm fayllari yuklanishi mumkin")
        return value

    def create(self, validated_data):
        images_data = validated_data.pop("images_data", [])
        place = Place.objects.create(**validated_data)
        for i, image in enumerate(images_data):
            PlaceImage.objects.create(place=place, image=image, is_primary=(i == 0))
        return place

    def update(self, instance, validated_data):
        images_data = validated_data.pop("images_data", None)
        place = super().update(instance, validated_data)
        if images_data:
            place.images.all().delete()
            for i, image in enumerate(images_data):
                PlaceImage.objects.create(place=place, image=image, is_primary=(i == 0))
        return place


class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ["id", "slots_free", "recorded_at"]
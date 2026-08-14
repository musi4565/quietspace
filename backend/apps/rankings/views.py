from django.db.models import Avg, Count
from rest_framework import generics, permissions, serializers
from rest_framework.response import Response

from apps.places.models import Place, PlaceStatus
from apps.places.serializers import PlaceListSerializer


class _RankedPlaceSerializer(PlaceListSerializer):
    ranking_value = serializers.SerializerMethodField()

    class Meta(PlaceListSerializer.Meta):
        fields = PlaceListSerializer.Meta.fields + ["ranking_value"]

    def get_ranking_value(self, obj):
        if hasattr(obj, "ranking_value"):
            return obj.ranking_value
        return None


class RankingListView(generics.ListAPIView):
    """Reytinglar: eng yaxshi, eng tinch, eng yaxshi wifi, eng qulay."""

    serializer_class = PlaceListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def list(self, request, *args, **kwargs):
        base = (
            Place.objects.filter(status=PlaceStatus.APPROVED)
            .select_related("district")
            .prefetch_related("images")
        )

        categories = []

        best = (
            base.annotate(avg_rating=Avg("reviews__rating"), rating_count=Count("reviews"))
            .filter(rating_count__gt=0)
            .order_by("-avg_rating", "-rating_count")[:10]
        )
        categories.append({"category": "best", "title": "🏆 Eng yaxshi joylar", "places": self._dump(best, "avg_rating")})

        quiet = base.filter(noise_level__in=["VERY_QUIET", "QUIET"]).order_by("noise_level", "price_per_hour")[:10]
        categories.append({"category": "quiet", "title": "🤫 Eng tinch", "places": self._dump(quiet, "noise")})

        wifi = base.order_by("-wifi_speed")[:10]
        categories.append({"category": "wifi", "title": "📶 Eng yaxshi Wi-Fi", "places": self._dump(wifi, "wifi_speed")})

        comfy = base.order_by("-socket_count", "-wifi_speed")[:10]
        categories.append({"category": "comfort", "title": "🔌 Eng qulay", "places": self._dump(comfy, "comfort")})

        return Response({"success": True, "categories": categories})

    def _dump(self, qs, ranking_value):
        for place in qs:
            place.ranking_value = getattr(place, ranking_value, None)
        return _RankedPlaceSerializer(qs, many=True, context={"request": self.request}).data
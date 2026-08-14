from django.db.models import Avg, Count
from rest_framework import filters, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdminUser, IsPlaceOwner
from apps.places.models import Availability, District, Place, PlaceStatus
from apps.places.serializers import (
    AvailabilitySerializer,
    DistrictSerializer,
    PlaceDetailSerializer,
    PlaceListSerializer,
)


class PlaceListView(generics.ListAPIView):
    """Approved joylar - qidiruv, filter, pagination."""

    serializer_class = PlaceListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "description", "address", "district__name"]

    def get_queryset(self):
        qs = (
            Place.objects.filter(status=PlaceStatus.APPROVED)
            .select_related("district")
            .prefetch_related("images")
            .annotate(
                avg_rating=Avg("reviews__rating"),
                rating_count=Count("reviews"),
            )
        )

        district = self.request.query_params.get("district")
        if district:
            qs = qs.filter(district__slug=district)

        price = self.request.query_params.get("price")
        if price:
            if price == "free":
                qs = qs.filter(price_per_hour=0)
            elif price == "under_50k":
                qs = qs.filter(price_per_hour__lte=50000)
            elif price == "under_100k":
                qs = qs.filter(price_per_hour__lte=100000)

        noise = self.request.query_params.get("noise")
        if noise:
            qs = qs.filter(noise_level__in=noise.split(","))

        wifi = self.request.query_params.get("wifi")
        if wifi == "good":
            qs = qs.filter(wifi_speed__gte=20)
        elif wifi == "excellent":
            qs = qs.filter(wifi_speed__gte=50)

        sockets = self.request.query_params.get("sockets")
        if sockets in ("true", "1"):
            qs = qs.filter(socket_count__gt=0)
        elif sockets in ("false", "0"):
            qs = qs.filter(socket_count=0)

        available = self.request.query_params.get("available")
        if available in ("true", "1"):
            qs = qs.filter(available_slots__gt=0)

        ordering = self.request.query_params.get("ordering")
        if ordering == "rating":
            qs = qs.order_by("-avg_rating")
        elif ordering == "price":
            qs = qs.order_by("price_per_hour")
        else:
            qs = qs.order_by("-is_featured", "-created_at")

        return qs


class PlaceDetailView(generics.RetrieveAPIView):
    serializer_class = PlaceDetailSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Place.objects.select_related("district").prefetch_related("images").annotate(
            avg_rating=Avg("reviews__rating"),
            rating_count=Count("reviews"),
        )
        user = self.request.user
        if user.is_authenticated and (user.is_admin or user.is_place_owner):
            return qs
        return qs.filter(status=PlaceStatus.APPROVED)


class MyPlacesView(generics.ListAPIView):
    """Owner o'z joylarini ko'radi (approve qilinmaganlar ham)."""

    serializer_class = PlaceListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Place.objects.filter(owner=self.request.user)
            .select_related("district")
            .prefetch_related("images")
            .annotate(avg_rating=Avg("reviews__rating"), rating_count=Count("reviews"))
        )


class CreatePlaceView(generics.CreateAPIView):
    serializer_class = PlaceDetailSerializer
    permission_classes = [IsPlaceOwner]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, status=PlaceStatus.PENDING)


class ApprovePlaceView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            place = Place.objects.get(pk=pk, status=PlaceStatus.PENDING)
        except Place.DoesNotExist:
            return Response({"success": False, "message": "Joy topilmadi"}, status=status.HTTP_404_NOT_FOUND)
        place.status = PlaceStatus.APPROVED
        place.save(update_fields=["status", "updated_at"])
        from apps.notifications.services import notify_new_approved_place

        notify_new_approved_place(place)
        return Response({"success": True, "message": "Joy tasdiqlandi"})


class RejectPlaceView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            place = Place.objects.get(pk=pk, status=PlaceStatus.PENDING)
        except Place.DoesNotExist:
            return Response({"success": False, "message": "Joy topilmadi"}, status=status.HTTP_404_NOT_FOUND)
        place.status = PlaceStatus.REJECTED
        place.save(update_fields=["status", "updated_at"])
        return Response({"success": True, "message": "Joy rad etildi"})


class AdminPlaceListView(generics.ListAPIView):
    serializer_class = PlaceListSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "address"]

    def get_queryset(self):
        qs = (
            Place.objects.select_related("district")
            .prefetch_related("images")
            .annotate(avg_rating=Avg("reviews__rating"), rating_count=Count("reviews"))
        )
        stat = self.request.query_params.get("status")
        if stat in PlaceStatus.values:
            qs = qs.filter(status=stat)
        return qs


class AdminPlaceUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PlaceDetailSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Place.objects.select_related("district").prefetch_related("images")


class DistrictListView(generics.ListAPIView):
    serializer_class = DistrictSerializer
    permission_classes = [permissions.AllowAny]
    queryset = District.objects.all()
    pagination_class = None


class AvailabilityUpdateView(APIView):
    """Joy egasi bo'sh joylar sonini yangilaydi."""

    permission_classes = [IsPlaceOwner]

    def post(self, request, pk):
        try:
            place = Place.objects.get(pk=pk, owner=request.user)
        except Place.DoesNotExist:
            return Response(
                {"success": False, "message": "Joy topilmadi yoki sizga tegishli emas"},
                status=status.HTTP_404_NOT_FOUND,
            )
        slots = request.data.get("available_slots")
        if slots is None:
            return Response(
                {"success": False, "message": "available_slots kerak"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            slots = int(slots)
        except (TypeError, ValueError):
            return Response(
                {"success": False, "message": "available_slots butun son bo'lishi kerak"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if slots < 0 or slots > place.capacity:
            return Response(
                {"success": False, "message": "Bo'sh joylar 0 dan capacity gacha bo'lishi kerak"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        place.available_slots = slots
        place.save(update_fields=["available_slots", "updated_at"])
        Availability.objects.create(place=place, slots_free=slots)
        return Response({"success": True, "message": "Bo'sh joylar yangilandi", "available_slots": slots})


class AvailabilityHistoryView(generics.ListAPIView):
    serializer_class = AvailabilitySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Availability.objects.filter(place_id=self.kwargs["pk"])[:50]
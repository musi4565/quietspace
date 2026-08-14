from django.db.models import Count
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Role, User
from apps.core.permissions import IsAdminUser
from apps.favorites.models import Favorite
from apps.notifications.models import NotificationSubscription
from apps.panel.serializers import AdminUserListSerializer, AdminUserUpdateSerializer
from apps.places.models import Place, PlaceStatus
from apps.reviews.models import Review


class DashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = {
            "users": User.objects.count(),
            "place_owners": User.objects.filter(role=Role.PLACE_OWNER).count(),
            "places": Place.objects.count(),
            "pending_places": Place.objects.filter(status=PlaceStatus.PENDING).count(),
            "approved_places": Place.objects.filter(status=PlaceStatus.APPROVED).count(),
            "reviews": Review.objects.count(),
            "favorites": Favorite.objects.count(),
            "subscriptions": NotificationSubscription.objects.count(),
        }
        return Response({"success": True, **data})


class AdminUserListView(generics.ListAPIView):
    serializer_class = AdminUserListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = User.objects.annotate(place_count=Count("owned_places"))
        role = self.request.query_params.get("role")
        if role in Role.values:
            qs = qs.filter(role=role)
        return qs


class AdminUserDetailView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"success": False, "message": "User topilmadi"}, status=status.HTTP_404_NOT_FOUND)
        if user.is_superuser:
            return Response(
                {"success": False, "message": "Superuserni o'zgartirib bo'lmaydi"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = AdminUserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "message": "User yangilandi"})


class AdminReviewListView(generics.ListAPIView):
    from apps.reviews.serializers import ReviewSerializer

    serializer_class = ReviewSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Review.objects.select_related("user", "place")


class AdminSubscriptionListView(generics.ListAPIView):
    from apps.notifications.serializers import NotificationSubscriptionSerializer

    serializer_class = NotificationSubscriptionSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return NotificationSubscription.objects.select_related("district", "user")
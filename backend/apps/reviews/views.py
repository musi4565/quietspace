from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.places.models import Place, PlaceStatus
from apps.reviews.models import Review
from apps.reviews.serializers import ReviewCreateSerializer, ReviewSerializer


class PlaceReviewsView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Review.objects.filter(place_id=self.kwargs["place_id"]).select_related("user", "place")


class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        place_id = self.kwargs["place_id"]
        place = Place.objects.filter(pk=place_id, status=PlaceStatus.APPROVED).first()
        if not place:
            raise NotFound("Joy topilmadi")
        if Review.objects.filter(user=self.request.user, place=place).exists():
            from rest_framework.exceptions import ValidationError

            raise ValidationError({"place": "Siz bu joyga allaqachon baho bergansiz"})
        serializer.save(place=place)


class UserReviewsView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user).select_related("place")


class ReviewDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return Response({"success": False, "message": "Baho topilmadi"}, status=status.HTTP_404_NOT_FOUND)
        if review.user != request.user and not request.user.is_admin:
            return Response(
                {"success": False, "message": "Bu bahoni o'chirishga huquqingiz yo'q"},
                status=status.HTTP_403_FORBIDDEN,
            )
        review.delete()
        return Response({"success": True, "message": "Baho o'chirildi"})
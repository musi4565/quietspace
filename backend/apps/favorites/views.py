from django.db.models import Avg, Count
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.favorites.models import Favorite
from apps.favorites.serializers import FavoriteCreateSerializer, FavoritePlaceSerializer
from apps.places.models import Place


class FavoriteListView(generics.ListAPIView):
    serializer_class = FavoritePlaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Favorite.objects.filter(user=self.request.user)
            .select_related("place", "place__district")
            .prefetch_related("place__images")
        )


class FavoriteAddView(generics.CreateAPIView):
    serializer_class = FavoriteCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class FavoriteRemoveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, place_id):
        deleted, _ = Favorite.objects.filter(user=request.user, place_id=place_id).delete()
        if not deleted:
            return Response({"success": False, "message": "Sevimli topilmadi"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"success": True, "message": "Sevimlilardan olib tashlandi"})


class FavoriteStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, place_id):
        exists = Favorite.objects.filter(user=request.user, place_id=place_id).exists()
        return Response({"success": True, "is_favorite": exists})


class FavoritePlaceIdsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        ids = list(Favorite.objects.filter(user=request.user).values_list("place_id", flat=True))
        return Response({"success": True, "place_ids": ids})
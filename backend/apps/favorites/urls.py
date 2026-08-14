from django.urls import path

from apps.favorites.views import (
    FavoriteAddView,
    FavoriteListView,
    FavoritePlaceIdsView,
    FavoriteRemoveView,
    FavoriteStatusView,
)

urlpatterns = [
    path("", FavoriteListView.as_view(), name="favorite-list"),
    path("ids/", FavoritePlaceIdsView.as_view(), name="favorite-ids"),
    path("add/", FavoriteAddView.as_view(), name="favorite-add"),
    path("remove/<int:place_id>/", FavoriteRemoveView.as_view(), name="favorite-remove"),
    path("status/<int:place_id>/", FavoriteStatusView.as_view(), name="favorite-status"),
]
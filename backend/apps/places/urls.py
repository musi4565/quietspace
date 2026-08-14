from django.urls import path

from apps.places.views import (
    AdminPlaceListView,
    AdminPlaceUpdateDeleteView,
    ApprovePlaceView,
    AvailabilityHistoryView,
    AvailabilityUpdateView,
    CreatePlaceView,
    DistrictListView,
    MyPlacesView,
    PlaceDetailView,
    PlaceListView,
    RejectPlaceView,
)

urlpatterns = [
    path("", PlaceListView.as_view(), name="place-list"),
    path("districts/", DistrictListView.as_view(), name="district-list"),
    path("mine/", MyPlacesView.as_view(), name="my-places"),
    path("create/", CreatePlaceView.as_view(), name="place-create"),
    path("admin/", AdminPlaceListView.as_view(), name="admin-place-list"),
    path("admin/<int:pk>/", AdminPlaceUpdateDeleteView.as_view(), name="admin-place-detail"),
    path("admin/<int:pk>/approve/", ApprovePlaceView.as_view(), name="place-approve"),
    path("admin/<int:pk>/reject/", RejectPlaceView.as_view(), name="place-reject"),
    path("<int:pk>/", PlaceDetailView.as_view(), name="place-detail"),
    path("<int:pk>/availability/", AvailabilityUpdateView.as_view(), name="place-availability"),
    path("<int:pk>/availability/history/", AvailabilityHistoryView.as_view(), name="place-availability-history"),
]
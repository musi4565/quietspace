from django.urls import path

from apps.reviews.views import PlaceReviewsView, ReviewCreateView, ReviewDeleteView, UserReviewsView

urlpatterns = [
    path("place/<int:place_id>/", PlaceReviewsView.as_view(), name="place-reviews"),
    path("place/<int:place_id>/create/", ReviewCreateView.as_view(), name="review-create"),
    path("mine/", UserReviewsView.as_view(), name="my-reviews"),
    path("<int:pk>/", ReviewDeleteView.as_view(), name="review-delete"),
]
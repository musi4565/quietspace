from django.urls import path

from apps.panel.views import (
    AdminReviewListView,
    AdminSubscriptionListView,
    AdminUserDetailView,
    AdminUserListView,
    DashboardView,
)

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="panel-dashboard"),
    path("users/", AdminUserListView.as_view(), name="panel-users"),
    path("users/<int:pk>/", AdminUserDetailView.as_view(), name="panel-user-detail"),
    path("reviews/", AdminReviewListView.as_view(), name="panel-reviews"),
    path("subscriptions/", AdminSubscriptionListView.as_view(), name="panel-subscriptions"),
]
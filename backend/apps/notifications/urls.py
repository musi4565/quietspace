from django.urls import path

from apps.notifications.views import (
    SubscriptionCreateView,
    SubscriptionDeleteView,
    SubscriptionListView,
    TelegramSubscriptionView,
)

urlpatterns = [
    path("", SubscriptionListView.as_view(), name="subscription-list"),
    path("create/", SubscriptionCreateView.as_view(), name="subscription-create"),
    path("telegram/", TelegramSubscriptionView.as_view(), name="subscription-telegram"),
    path("<int:pk>/", SubscriptionDeleteView.as_view(), name="subscription-delete"),
]
from django.urls import path

from apps.telegram.views import (
    BotFavoritesView,
    BotNotificationsToggleView,
    LinkConfirmView,
    LinkRequestView,
    MyTelegramProfileView,
)

urlpatterns = [
    path("link/request/", LinkRequestView.as_view(), name="telegram-link-request"),
    path("link/confirm/", LinkConfirmView.as_view(), name="telegram-link-confirm"),
    path("profile/", MyTelegramProfileView.as_view(), name="telegram-profile"),
    path("favorites/", BotFavoritesView.as_view(), name="telegram-bot-favorites"),
    path("notifications/", BotNotificationsToggleView.as_view(), name="telegram-bot-notifications"),
]
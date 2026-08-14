from django.urls import path

from apps.telegram.views import LinkConfirmView, LinkRequestView, MyTelegramProfileView

urlpatterns = [
    path("link/request/", LinkRequestView.as_view(), name="telegram-link-request"),
    path("link/confirm/", LinkConfirmView.as_view(), name="telegram-link-confirm"),
    path("profile/", MyTelegramProfileView.as_view(), name="telegram-profile"),
]
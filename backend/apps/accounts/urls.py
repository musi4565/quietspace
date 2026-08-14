from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views import BecomePlaceOwnerView, LoginView, LogoutView, MeView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("become-place-owner/", BecomePlaceOwnerView.as_view(), name="become-place-owner"),
]
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.serializers import ProfileUpdateSerializer, RegisterSerializer, UserSerializer
from apps.accounts.models import Role


def _tokens_for(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"success": True, "message": "Ro'yxatdan o'tish muvaffaqiyatli", "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenObtainPairSerializer(
            data={"email": request.data.get("email"), "password": request.data.get("password")}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        tokens = _tokens_for(user)
        return Response(
            {
                "success": True,
                "message": "Tizimga kirish muvaffaqiyatli",
                "user": UserSerializer(user).data,
                **tokens,
            }
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"success": True, "user": UserSerializer(request.user).data})

    def patch(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "user": UserSerializer(request.user).data})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except Exception:
                pass
        return Response({"success": True, "message": "Chiqildi"})


class BecomePlaceOwnerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.role = Role.PLACE_OWNER
        user.save(update_fields=["role"])
        return Response(
            {"success": True, "message": "Endi siz joy egasi (PLACE_OWNER) roliga o'tdingiz", "user": UserSerializer(user).data}
        )
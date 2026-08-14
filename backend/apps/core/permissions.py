from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """Faqat ADMIN rolidagi userlar."""

    message = "Bu amal uchun admin huquqi kerak."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "ADMIN"
        )


class IsPlaceOwner(BasePermission):
    """Faqat PLACE_OWNER rolidagi userlar."""

    message = "Bu amal uchun joy egasi huquqi kerak."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "PLACE_OWNER"
        )
import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.accounts.models import User


class TelegramLinkCode(models.Model):
    """One-time, qisqa muddatli bog'lash kodi (sayt user <-> telegram chat)."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="telegram_link_codes")
    code = models.CharField(max_length=32, unique=True, db_index=True)
    telegram_chat_id = models.CharField(max_length=100, blank=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @classmethod
    def create_for(cls, user, ttl_minutes: int = 10):
        return cls.objects.create(
            user=user,
            code=secrets.token_urlsafe(24),
            expires_at=timezone.now() + timezone.timedelta(minutes=ttl_minutes),
        )

    def is_valid(self) -> bool:
        return not self.is_used and self.expires_at > timezone.now()

    def link_url(self) -> str:
        return f"{settings.FRONTEND_URL}/telegram-link?code={self.code}"


class TelegramProfile(models.Model):
    """Telegram chat <-> sayt user bog'lanishi."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="telegram_profile")
    chat_id = models.CharField(max_length=100, unique=True, db_index=True)
    username = models.CharField(max_length=100, blank=True)
    notifications_enabled = models.BooleanField(default=True)
    linked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} <-> tg {self.chat_id}"
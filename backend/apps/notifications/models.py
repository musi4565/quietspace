from django.db import models

from apps.accounts.models import User
from apps.places.models import District


class NotificationSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="notification_subscriptions")
    telegram_chat_id = models.CharField(max_length=100, blank=True, db_index=True)
    telegram_username = models.CharField(max_length=100, blank=True)

    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    max_price = models.PositiveIntegerField(null=True, blank=True)
    noise_level = models.CharField(max_length=20, blank=True)
    wifi_min = models.PositiveIntegerField(null=True, blank=True)
    sockets_required = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        target = self.telegram_chat_id or (self.user.email if self.user else "-")
        return f"Subscription ({target})"

    def matches(self, place) -> bool:
        if not self.is_active:
            return False
        if self.district_id and place.district_id != self.district_id:
            return False
        if self.max_price is not None and place.price_per_hour > self.max_price:
            return False
        if self.noise_level and place.noise_level != self.noise_level:
            return False
        if self.wifi_min and place.wifi_speed < self.wifi_min:
            return False
        if self.sockets_required and place.socket_count == 0:
            return False
        return True
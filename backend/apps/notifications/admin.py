from django.contrib import admin

from apps.notifications.models import NotificationSubscription


@admin.register(NotificationSubscription)
class NotificationSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "telegram_chat_id", "district", "max_price", "is_active", "created_at"]
    list_filter = ["is_active", "district", "noise_level"]
from django.contrib import admin

from apps.telegram.models import TelegramLinkCode, TelegramProfile


@admin.register(TelegramLinkCode)
class TelegramLinkCodeAdmin(admin.ModelAdmin):
    list_display = ["user", "code", "is_used", "expires_at", "created_at"]
    list_filter = ["is_used"]


@admin.register(TelegramProfile)
class TelegramProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "chat_id", "username", "linked_at"]
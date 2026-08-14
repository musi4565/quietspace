from django.contrib import admin

from apps.reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["user", "place", "rating", "noise_feedback", "wifi_feedback", "created_at"]
    list_filter = ["rating", "noise_feedback", "wifi_feedback"]
    search_fields = ["user__email", "place__name", "text"]
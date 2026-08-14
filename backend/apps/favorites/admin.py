from django.contrib import admin

from apps.favorites.models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ["user", "place", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__email", "place__name"]
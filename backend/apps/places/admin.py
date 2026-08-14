from django.contrib import admin

from apps.places.models import Availability, District, Place, PlaceImage


class PlaceImageInline(admin.TabularInline):
    model = PlaceImage
    extra = 1


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name"]


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ["name", "district", "status", "price_per_hour", "available_slots", "wifi_speed", "owner"]
    list_filter = ["status", "district", "noise_level"]
    search_fields = ["name", "address"]
    inlines = [PlaceImageInline]
    actions = ["approve_selected"]

    @admin.action(description="Tasdiqlash (APPROVED)")
    def approve_selected(self, request, queryset):
        updated = queryset.update(status="APPROVED")
        self.message_user(request, f"{updated} ta joy tasdiqlandi")


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ["place", "slots_free", "recorded_at"]
    list_filter = ["recorded_at"]
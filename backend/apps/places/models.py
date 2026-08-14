from django.db import models

from apps.accounts.models import User


class NoiseLevel(models.TextChoices):
    VERY_QUIET = "VERY_QUIET", "Juda tinch"
    QUIET = "QUIET", "Tinch"
    AVERAGE = "AVERAGE", "O'rtacha"
    NOISY = "NOISY", "Shovqinli"


class WifiFeedback(models.TextChoices):
    EXCELLENT = "EXCELLENT", "Juda yaxshi"
    GOOD = "GOOD", "Yaxshi"
    AVERAGE = "AVERAGE", "O'rtacha"
    POOR = "POOR", "Yomon"


class PlaceStatus(models.TextChoices):
    PENDING = "PENDING", "Kutilmoqda"
    APPROVED = "APPROVED", "Tasdiqlangan"
    REJECTED = "REJECTED", "Rad etilgan"


class District(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.name.lower().replace(" ", "-").replace("'", "")
        super().save(*args, **kwargs)


class Place(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    district = models.ForeignKey(District, on_delete=models.PROTECT, related_name="places")
    address = models.CharField(max_length=300)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    price_per_hour = models.PositiveIntegerField(default=0, help_text="so'mda, 0 = bepul")
    wifi_speed = models.PositiveIntegerField(default=0, help_text="Mbps")
    socket_count = models.PositiveIntegerField(default=0, help_text="rozetkalar soni")
    noise_level = models.CharField(max_length=20, choices=NoiseLevel.choices, default=NoiseLevel.AVERAGE)
    capacity = models.PositiveIntegerField(default=10, help_text="maksimal sig'im")
    available_slots = models.PositiveIntegerField(default=0, help_text="hozirgi bo'sh joylar")

    open_time = models.TimeField(default="08:00")
    close_time = models.TimeField(default="22:00")

    status = models.CharField(
        max_length=20, choices=PlaceStatus.choices, default=PlaceStatus.PENDING, db_index=True
    )
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="owned_places"
    )
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "district"]),
            models.Index(fields=["status", "noise_level"]),
        ]

    def __str__(self):
        return self.name


class PlaceImage(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="places/")
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_primary", "uploaded_at"]

    def __str__(self):
        return f"{self.place.name} image #{self.pk}"


class Availability(models.Model):
    """Real-time availability history - WebSocket kelajagi uchun mo'ljallangan."""

    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="availability_log")
    slots_free = models.PositiveIntegerField()
    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.place.name}: {self.slots_free} bo'sh ({self.recorded_at:%H:%M})"
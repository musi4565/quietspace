from django.db import models

from apps.accounts.models import User
from apps.places.models import Place


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    text = models.TextField(blank=True)
    noise_feedback = models.CharField(max_length=20, blank=True)
    wifi_feedback = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "place"], name="unique_review_user_place")
        ]
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["place", "rating"])]

    def __str__(self):
        return f"{self.user.email} -> {self.place.name}: {self.rating}*"
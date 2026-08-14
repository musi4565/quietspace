from django.db import models

from apps.accounts.models import User
from apps.places.models import Place


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "place"], name="unique_favorite_user_place")
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} -> {self.place.name}"
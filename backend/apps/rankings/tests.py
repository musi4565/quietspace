from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.places.models import District, NoiseLevel, Place, PlaceStatus
from apps.reviews.models import Review

User = get_user_model()


class RankingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="rank@test.uz", password="RankPass123", full_name="Rank")
        self.district = District.objects.get_or_create(name="Yunusobod", defaults={"slug": "yunusobod"})[0]
        self.best = Place.objects.create(
            name="Best Place", district=self.district, address="a", latitude=41.3, longitude=69.2,
            wifi_speed=100, socket_count=20, noise_level=NoiseLevel.VERY_QUIET, status=PlaceStatus.APPROVED,
        )
        self.worst = Place.objects.create(
            name="Worst Place", district=self.district, address="b", latitude=41.3, longitude=69.2,
            wifi_speed=5, socket_count=0, noise_level=NoiseLevel.NOISY, status=PlaceStatus.APPROVED,
        )

    def test_rankings_categories(self):
        resp = self.client.get("/api/rankings/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        cats = {c["category"] for c in resp.data["categories"]}
        self.assertEqual(cats, {"best", "quiet", "wifi", "comfort"})

    def test_wifi_ranking_order(self):
        resp = self.client.get("/api/rankings/")
        wifi_cat = next(c for c in resp.data["categories"] if c["category"] == "wifi")
        self.assertEqual(wifi_cat["places"][0]["name"], "Best Place")

    def test_best_ranking_by_rating(self):
        login = self.client.post(
            "/api/auth/login/", {"email": "rank@test.uz", "password": "RankPass123"}, format="json"
        )
        auth = f"Bearer {login.data['access']}"
        self.client.post(
            f"/api/reviews/place/{self.best.id}/create/",
            {"rating": 5}, format="json", HTTP_AUTHORIZATION=auth,
        )
        resp = self.client.get("/api/rankings/")
        best_cat = next(c for c in resp.data["categories"] if c["category"] == "best")
        self.assertEqual(best_cat["places"][0]["name"], "Best Place")
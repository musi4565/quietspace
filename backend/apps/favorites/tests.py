from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.favorites.models import Favorite
from apps.places.models import District, Place, PlaceStatus

User = get_user_model()


class FavoriteTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="fav@test.uz", password="FavPass123", full_name="Fav")
        self.district = District.objects.get_or_create(name="Mirobod", defaults={"slug": "mirobod"})[0]
        self.place = Place.objects.create(
            name="Cozy Corner",
            district=self.district,
            address="addr",
            latitude=41.2,
            longitude=69.2,
            status=PlaceStatus.APPROVED,
        )
        login = self.client.post(
            "/api/auth/login/", {"email": "fav@test.uz", "password": "FavPass123"}, format="json"
        )
        self.auth = f"Bearer {login.data['access']}"

    def test_add_favorite(self):
        resp = self.client.post(
            "/api/favorites/add/", {"place": self.place.id}, format="json", HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Favorite.objects.filter(user=self.user, place=self.place).exists())

    def test_add_favorite_duplicate_blocked(self):
        self.client.post(
            "/api/favorites/add/", {"place": self.place.id}, format="json", HTTP_AUTHORIZATION=self.auth
        )
        resp = self.client.post(
            "/api/favorites/add/", {"place": self.place.id}, format="json", HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_favorite_requires_auth(self):
        resp = self.client.post("/api/favorites/add/", {"place": self.place.id}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_favorite_list(self):
        self.client.post(
            "/api/favorites/add/", {"place": self.place.id}, format="json", HTTP_AUTHORIZATION=self.auth
        )
        resp = self.client.get("/api/favorites/", HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["results"]), 1)

    def test_favorite_status(self):
        self.client.post(
            "/api/favorites/add/", {"place": self.place.id}, format="json", HTTP_AUTHORIZATION=self.auth
        )
        resp = self.client.get(f"/api/favorites/status/{self.place.id}/", HTTP_AUTHORIZATION=self.auth)
        self.assertTrue(resp.data["is_favorite"])

    def test_favorite_remove(self):
        self.client.post(
            "/api/favorites/add/", {"place": self.place.id}, format="json", HTTP_AUTHORIZATION=self.auth
        )
        resp = self.client.delete(
            f"/api/favorites/remove/{self.place.id}/", HTTP_AUTHORIZATION=self.auth
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(Favorite.objects.filter(user=self.user, place=self.place).exists())
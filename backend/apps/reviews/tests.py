from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.places.models import District, Place, PlaceStatus
from apps.reviews.models import Review

User = get_user_model()


class ReviewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="rev@test.uz", password="RevPass123", full_name="Rev")
        self.district = District.objects.get_or_create(name="Olmazor", defaults={"slug": "olamazor"})[0]
        self.place = Place.objects.create(
            name="Green Cafe",
            district=self.district,
            address="addr",
            latitude=41.2,
            longitude=69.2,
            status=PlaceStatus.APPROVED,
        )
        login = self.client.post(
            "/api/auth/login/", {"email": "rev@test.uz", "password": "RevPass123"}, format="json"
        )
        self.auth = f"Bearer {login.data['access']}"

    def test_create_review(self):
        resp = self.client.post(
            f"/api/reviews/place/{self.place.id}/create/",
            {"rating": 5, "text": "Zo'r joy", "noise_feedback": "VERY_QUIET", "wifi_feedback": "EXCELLENT"},
            format="json",
            HTTP_AUTHORIZATION=self.auth,
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Review.objects.filter(user=self.user, place=self.place).exists())

    def test_create_review_duplicate_blocked(self):
        self.client.post(
            f"/api/reviews/place/{self.place.id}/create/",
            {"rating": 5},
            format="json",
            HTTP_AUTHORIZATION=self.auth,
        )
        resp = self.client.post(
            f"/api/reviews/place/{self.place.id}/create/",
            {"rating": 4},
            format="json",
            HTTP_AUTHORIZATION=self.auth,
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_invalid_rating(self):
        resp = self.client.post(
            f"/api/reviews/place/{self.place.id}/create/",
            {"rating": 9},
            format="json",
            HTTP_AUTHORIZATION=self.auth,
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_review_invalid_feedback(self):
        resp = self.client.post(
            f"/api/reviews/place/{self.place.id}/create/",
            {"rating": 5, "noise_feedback": "INVALID"},
            format="json",
            HTTP_AUTHORIZATION=self.auth,
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_place_reviews_list(self):
        self.client.post(
            f"/api/reviews/place/{self.place.id}/create/",
            {"rating": 4},
            format="json",
            HTTP_AUTHORIZATION=self.auth,
        )
        resp = self.client.get(f"/api/reviews/place/{self.place.id}/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["results"]), 1)

    def test_avg_rating_in_detail(self):
        self.client.post(
            f"/api/reviews/place/{self.place.id}/create/",
            {"rating": 5},
            format="json",
            HTTP_AUTHORIZATION=self.auth,
        )
        user2 = User.objects.create_user(email="rev2@test.uz", password="RevPass123", full_name="Rev2")
        login2 = self.client.post(
            "/api/auth/login/", {"email": "rev2@test.uz", "password": "RevPass123"}, format="json"
        )
        self.client.post(
            f"/api/reviews/place/{self.place.id}/create/",
            {"rating": 4},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {login2.data['access']}",
        )
        resp = self.client.get(f"/api/places/{self.place.id}/")
        self.assertEqual(resp.data["avg_rating"], 4.5)
        self.assertEqual(resp.data["rating_count"], 2)

    def test_review_delete_only_owner(self):
        created = self.client.post(
            f"/api/reviews/place/{self.place.id}/create/",
            {"rating": 3},
            format="json",
            HTTP_AUTHORIZATION=self.auth,
        )
        other = User.objects.create_user(email="other@test.uz", password="OtherPass123", full_name="Other")
        login = self.client.post(
            "/api/auth/login/", {"email": "other@test.uz", "password": "OtherPass123"}, format="json"
        )
        resp = self.client.delete(
            f"/api/reviews/{created.data['id']}/", HTTP_AUTHORIZATION=f"Bearer {login.data['access']}"
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
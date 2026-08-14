from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Role
from apps.places.models import District, NoiseLevel, Place, PlaceImage, PlaceStatus

User = get_user_model()


class PlacesAPITests(APITestCase):
    def setUp(self):
        self.district = District.objects.get_or_create(name="Chilonzor", defaults={"slug": "chilonzor"})[0]
        self.passwords = {"owner@test.uz": "OwnerPass123", "admin@test.uz": "AdminPass123", "user@test.uz": "UserPass123"}
        self.owner = User.objects.create_user(
            email="owner@test.uz", password="OwnerPass123", full_name="Owner", role=Role.PLACE_OWNER
        )
        self.admin = User.objects.create_user(
            email="admin@test.uz", password="AdminPass123", full_name="Admin", role=Role.ADMIN
        )
        self.user = User.objects.create_user(
            email="user@test.uz", password="UserPass123", full_name="User"
        )
        self.approved = Place.objects.create(
            name="Quiet Coffee",
            district=self.district,
            address="Chilonzor 9",
            latitude=41.27,
            longitude=69.21,
            price_per_hour=30000,
            wifi_speed=85,
            socket_count=8,
            noise_level=NoiseLevel.QUIET,
            capacity=30,
            available_slots=12,
            status=PlaceStatus.APPROVED,
            owner=self.owner,
        )
        self.pending = Place.objects.create(
            name="Hidden Cafe",
            district=self.district,
            address="Chilonzor 10",
            latitude=41.28,
            longitude=69.22,
            price_per_hour=10000,
            wifi_speed=10,
            socket_count=0,
            noise_level=NoiseLevel.NOISY,
            capacity=10,
            available_slots=0,
            status=PlaceStatus.PENDING,
        )

    def _auth(self, user):
        return f"Bearer {self._token(user)}"

    def _token(self, user):
        resp = self.client.post(
            "/api/auth/login/",
            {"email": user.email, "password": self.passwords.get(user.email, "x")},
            format="json",
        )
        return resp.data["access"]

    def test_list_only_approved(self):
        resp = self.client.get("/api/places/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        names = [p["name"] for p in resp.data["results"]]
        self.assertIn("Quiet Coffee", names)
        self.assertNotIn("Hidden Cafe", names)

    def test_search_by_name(self):
        resp = self.client.get("/api/places/?search=Quiet")
        self.assertEqual(resp.data["count"], 1)
        self.assertEqual(resp.data["results"][0]["name"], "Quiet Coffee")

    def test_filter_district(self):
        resp = self.client.get("/api/places/?district=chilonzor")
        self.assertEqual(resp.data["count"], 1)

    def test_filter_price(self):
        resp = self.client.get("/api/places/?price=under_50k")
        self.assertEqual(resp.data["count"], 1)

    def test_filter_available(self):
        resp = self.client.get("/api/places/?available=true")
        self.assertEqual(resp.data["count"], 1)

    def test_filter_combined(self):
        resp = self.client.get("/api/places/?district=chilonzor&price=under_50k&noise=QUIET&wifi=good&sockets=true&available=true")
        self.assertEqual(resp.data["count"], 1)

    def test_pagination(self):
        for i in range(15):
            Place.objects.create(
                name=f"Place {i}",
                district=self.district,
                address="addr",
                latitude=41.0,
                longitude=69.0,
                status=PlaceStatus.APPROVED,
            )
        resp = self.client.get("/api/places/?page_size=10")
        self.assertEqual(len(resp.data["results"]), 10)
        self.assertIsNotNone(resp.data["next"])

    def test_detail_hidden_for_pending(self):
        resp = self.client.get(f"/api/places/{self.pending.id}/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_see_own_pending(self):
        resp = self.client.get(
            f"/api/places/{self.pending.id}/", HTTP_AUTHORIZATION=self._auth(self.owner)
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_only_owner_can_create_place(self):
        data = {
            "name": "New Cafe",
            "district_id": self.district.id,
            "address": "addr",
            "latitude": 41.1,
            "longitude": 69.1,
            "price_per_hour": 10000,
            "wifi_speed": 30,
            "socket_count": 2,
            "noise_level": "QUIET",
            "capacity": 20,
        }
        resp = self.client.post(
            "/api/places/create/", data, format="json", HTTP_AUTHORIZATION=self._auth(self.user)
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        resp = self.client.post(
            "/api/places/create/", data, format="json", HTTP_AUTHORIZATION=self._auth(self.owner)
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        place = Place.objects.get(name="New Cafe")
        self.assertEqual(place.status, PlaceStatus.PENDING)

    def test_admin_approve(self):
        place = Place.objects.create(
            name="Approve Me",
            district=self.district,
            address="addr",
            latitude=41.2,
            longitude=69.2,
            status=PlaceStatus.PENDING,
        )
        resp = self.client.post(
            f"/api/places/admin/{place.id}/approve/", HTTP_AUTHORIZATION=self._auth(self.admin)
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        place.refresh_from_db()
        self.assertEqual(place.status, PlaceStatus.APPROVED)

    def test_admin_approve_forbidden_for_user(self):
        place = Place.objects.create(
            name="Approve Me 2",
            district=self.district,
            address="addr",
            latitude=41.2,
            longitude=69.2,
            status=PlaceStatus.PENDING,
        )
        resp = self.client.post(
            f"/api/places/admin/{place.id}/approve/", HTTP_AUTHORIZATION=self._auth(self.user)
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_reject(self):
        place = Place.objects.create(
            name="Reject Me",
            district=self.district,
            address="addr",
            latitude=41.2,
            longitude=69.2,
            status=PlaceStatus.PENDING,
        )
        resp = self.client.post(
            f"/api/places/admin/{place.id}/reject/", HTTP_AUTHORIZATION=self._auth(self.admin)
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        place.refresh_from_db()
        self.assertEqual(place.status, PlaceStatus.REJECTED)

    def test_availability_update(self):
        resp = self.client.post(
            f"/api/places/{self.approved.id}/availability/",
            {"available_slots": 5},
            format="json",
            HTTP_AUTHORIZATION=self._auth(self.owner),
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.approved.refresh_from_db()
        self.assertEqual(self.approved.available_slots, 5)

    def test_availability_update_not_owner(self):
        resp = self.client.post(
            f"/api/places/{self.approved.id}/availability/",
            {"available_slots": 5},
            format="json",
            HTTP_AUTHORIZATION=self._auth(self.user),
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_districts_list(self):
        resp = self.client.get("/api/places/districts/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("Chilonzor", [d["name"] for d in resp.data])

    def test_nearby_orders_by_distance(self):
        self.approved.latitude = 41.32
        self.approved.longitude = 69.28
        self.approved.save()
        far = Place.objects.create(
            name="Far Place",
            district=self.district,
            address="Boshqa joy",
            latitude=41.5,
            longitude=69.5,
            price_per_hour=10000,
            wifi_speed=40,
            socket_count=2,
            noise_level=NoiseLevel.AVERAGE,
            capacity=20,
            available_slots=5,
            status=PlaceStatus.APPROVED,
        )
        resp = self.client.get(f"/api/places/?lat=41.32&lng=69.28&page_size=10")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        results = resp.data["results"]
        self.assertGreaterEqual(len(results), 2)
        self.assertEqual(results[0]["id"], self.approved.id)
        self.assertIsNotNone(results[0]["distance_km"])
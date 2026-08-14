from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.notifications.models import NotificationSubscription
from apps.notifications.services import notify_new_approved_place
from apps.places.models import District, NoiseLevel, Place, PlaceStatus

User = get_user_model()


class NotificationSubscriptionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="sub@test.uz", password="SubPass123", full_name="Sub")
        self.district = District.objects.get_or_create(name="Chilonzor", defaults={"slug": "chilonzor"})[0]
        login = self.client.post(
            "/api/auth/login/", {"email": "sub@test.uz", "password": "SubPass123"}, format="json"
        )
        self.auth = f"Bearer {login.data['access']}"

    def test_create_subscription(self):
        resp = self.client.post(
            "/api/notifications/create/",
            {"district": self.district.id, "max_price": 50000, "noise_level": "QUIET"},
            format="json",
            HTTP_AUTHORIZATION=self.auth,
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(NotificationSubscription.objects.filter(user=self.user).exists())

    def test_list_subscriptions(self):
        self.client.post(
            "/api/notifications/create/",
            {"district": self.district.id},
            format="json",
            HTTP_AUTHORIZATION=self.auth,
        )
        resp = self.client.get("/api/notifications/", HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(len(resp.data["results"]), 1)

    def test_subscription_requires_auth(self):
        resp = self.client.post(
            "/api/notifications/create/", {"district": self.district.id}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_telegram_subscription(self):
        resp = self.client.post(
            "/api/notifications/telegram/",
            {"telegram_chat_id": "12345", "district": "chilonzor", "max_price": 30000},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(NotificationSubscription.objects.filter(telegram_chat_id="12345").exists())

    def test_matches(self):
        sub = NotificationSubscription.objects.create(
            user=self.user, district=self.district, max_price=50000, noise_level="QUIET", wifi_min=50, sockets_required=True
        )
        place = Place.objects.create(
            name="Match",
            district=self.district,
            address="a",
            latitude=41.2,
            longitude=69.2,
            price_per_hour=30000,
            wifi_speed=85,
            socket_count=8,
            noise_level=NoiseLevel.QUIET,
            status=PlaceStatus.APPROVED,
        )
        self.assertTrue(sub.matches(place))

        bad_place = Place.objects.create(
            name="No Match",
            district=self.district,
            address="b",
            latitude=41.2,
            longitude=69.2,
            price_per_hour=100000,
            wifi_speed=5,
            socket_count=0,
            noise_level=NoiseLevel.NOISY,
            status=PlaceStatus.APPROVED,
        )
        self.assertFalse(sub.matches(bad_place))

    @patch("apps.notifications.services.send_telegram_message", return_value=True)
    def test_notify_new_approved_place(self, mock_send):
        NotificationSubscription.objects.create(
            telegram_chat_id="999", district=self.district, max_price=40000
        )
        place = Place.objects.create(
            name="New",
            district=self.district,
            address="a",
            latitude=41.2,
            longitude=69.2,
            price_per_hour=20000,
            status=PlaceStatus.APPROVED,
        )
        sent = notify_new_approved_place(place)
        self.assertEqual(sent, 1)
        mock_send.assert_called_once()
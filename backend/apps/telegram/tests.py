from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.telegram.models import TelegramLinkCode, TelegramProfile

User = get_user_model()


class TelegramLinkTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="tg@test.uz", password="TgPass123", full_name="TG")
        login = self.client.post(
            "/api/auth/login/", {"email": "tg@test.uz", "password": "TgPass123"}, format="json"
        )
        self.auth = f"Bearer {login.data['access']}"

    def test_request_link_code(self):
        resp = self.client.post("/api/telegram/link/request/", HTTP_AUTHORIZATION=self.auth)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(resp.data["code"])
        self.assertTrue(TelegramLinkCode.objects.filter(user=self.user).exists())

    def test_request_requires_auth(self):
        resp = self.client.post("/api/telegram/link/request/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_confirm_link(self):
        link = TelegramLinkCode.create_for(self.user)
        resp = self.client.post(
            "/api/telegram/link/confirm/",
            {"code": link.code, "chat_id": "111222", "username": "testuser"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data["success"])
        profile = TelegramProfile.objects.get(chat_id="111222")
        self.assertEqual(profile.user, self.user)
        link.refresh_from_db()
        self.assertTrue(link.is_used)

    def test_confirm_invalid_code(self):
        resp = self.client.post(
            "/api/telegram/link/confirm/",
            {"code": "not-a-real-code", "chat_id": "111222"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_confirm_used_code_rejected(self):
        link = TelegramLinkCode.create_for(self.user)
        link.is_used = True
        link.save()
        resp = self.client.post(
            "/api/telegram/link/confirm/",
            {"code": link.code, "chat_id": "111222"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_expired_code_rejected(self):
        link = TelegramLinkCode.create_for(self.user)
        link.expires_at = timezone.now() - timezone.timedelta(minutes=1)
        link.save()
        resp = self.client.post(
            "/api/telegram/link/confirm/",
            {"code": link.code, "chat_id": "111222"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_my_profile(self):
        TelegramProfile.objects.create(user=self.user, chat_id="111", username="u")
        resp = self.client.get("/api/telegram/profile/", HTTP_AUTHORIZATION=self.auth)
        self.assertTrue(resp.data["linked"])
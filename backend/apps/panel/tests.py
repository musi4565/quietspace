from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Role

User = get_user_model()


class PanelTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="panel@test.uz", password="PanelPass123", full_name="Panel", role=Role.ADMIN
        )
        self.user = User.objects.create_user(email="normal@test.uz", password="NormalPass123", full_name="N")
        self.passwords = {"ADMIN": "PanelPass123", "USER": "NormalPass123"}
        self.admin_auth = f"Bearer {self._token(self.admin)}"
        self.user_auth = f"Bearer {self._token(self.user)}"

    def _token(self, user):
        resp = self.client.post(
            "/api/auth/login/",
            {"email": user.email, "password": self.passwords[user.role]},
            format="json",
        )
        return resp.data["access"]

    def test_dashboard_admin_only(self):
        resp = self.client.get("/api/panel/dashboard/", HTTP_AUTHORIZATION=self.user_auth)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        resp = self.client.get("/api/panel/dashboard/", HTTP_AUTHORIZATION=self.admin_auth)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("users", resp.data)

    def test_user_list(self):
        resp = self.client.get("/api/panel/users/", HTTP_AUTHORIZATION=self.admin_auth)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data["results"]), 2)

    def test_change_user_role(self):
        resp = self.client.patch(
            f"/api/panel/users/{self.user.id}/",
            {"role": "PLACE_OWNER"},
            format="json",
            HTTP_AUTHORIZATION=self.admin_auth,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, Role.PLACE_OWNER)

    def test_cannot_change_superuser(self):
        superuser = User.objects.create_superuser(email="root@test.uz", password="RootPass123", full_name="Root")
        resp = self.client.patch(
            f"/api/panel/users/{superuser.id}/",
            {"role": "USER"},
            format="json",
            HTTP_AUTHORIZATION=self.admin_auth,
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
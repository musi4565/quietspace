from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthFlowTests(APITestCase):
    def setUp(self):
        self.register_data = {
            "full_name": "Ali Valiyev",
            "email": "ali@test.uz",
            "password": "StrongPass123",
            "password_confirm": "StrongPass123",
        }

    def test_register_success(self):
        resp = self.client.post("/api/auth/register/", self.register_data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(resp.data["success"])
        self.assertEqual(resp.data["user"]["role"], "USER")
        self.assertTrue(User.objects.filter(email="ali@test.uz").exists())

    def test_register_password_mismatch(self):
        data = dict(self.register_data, password_confirm="Different123")
        resp = self.client.post("/api/auth/register/", data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(resp.data["success"])

    def test_register_short_password(self):
        data = dict(self.register_data, password="short", password_confirm="short")
        resp = self.client.post("/api/auth/register/", data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        self.client.post("/api/auth/register/", self.register_data, format="json")
        resp = self.client.post("/api/auth/register/", self.register_data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success_returns_jwt(self):
        self.client.post("/api/auth/register/", self.register_data, format="json")
        resp = self.client.post(
            "/api/auth/login/",
            {"email": "ali@test.uz", "password": "StrongPass123"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data["access"])
        self.assertTrue(resp.data["refresh"])

    def test_login_wrong_password(self):
        self.client.post("/api/auth/register/", self.register_data, format="json")
        resp = self.client.post(
            "/api/auth/login/",
            {"email": "ali@test.uz", "password": "WrongPass123"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_requires_auth(self):
        resp = self.client.get("/api/auth/me/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_with_token(self):
        self.client.post("/api/auth/register/", self.register_data, format="json")
        login = self.client.post(
            "/api/auth/login/",
            {"email": "ali@test.uz", "password": "StrongPass123"},
            format="json",
        )
        token = login.data["access"]
        resp = self.client.get("/api/auth/me/", HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["user"]["email"], "ali@test.uz")

    def test_jwt_refresh(self):
        self.client.post("/api/auth/register/", self.register_data, format="json")
        login = self.client.post(
            "/api/auth/login/",
            {"email": "ali@test.uz", "password": "StrongPass123"},
            format="json",
        )
        resp = self.client.post("/api/auth/refresh/", {"refresh": login.data["refresh"]}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data["access"])

    def test_become_place_owner(self):
        self.client.post("/api/auth/register/", self.register_data, format="json")
        login = self.client.post(
            "/api/auth/login/",
            {"email": "ali@test.uz", "password": "StrongPass123"},
            format="json",
        )
        token = login.data["access"]
        resp = self.client.post(
            "/api/auth/become-place-owner/", HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["user"]["role"], "PLACE_OWNER")
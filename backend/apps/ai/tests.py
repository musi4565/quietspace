from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.ai.services.matching import MatchingService
from apps.ai.services.parsers import RuleBasedParser
from apps.ai.services.requirements import PlaceRequirements
from apps.places.models import District, NoiseLevel, Place, PlaceStatus

User = get_user_model()


class ParserTests(APITestCase):
    def setUp(self):
        District.objects.get_or_create(name="Chilonzor", defaults={"slug": "chilonzor"})[0]
        District.objects.get_or_create(name="Yunusobod", defaults={"slug": "yunusobod"})[0]

    def test_parse_full_query(self):
        parser = RuleBasedParser()
        req = parser.parse(
            "Chilonzorda 3 soat ishlash uchun tinch, Wi-Fi tez, rozetkasi bor va 50 ming so'mdan arzon joy"
        )
        self.assertEqual(req.district, "chilonzor")
        self.assertEqual(req.noise, NoiseLevel.QUIET)
        self.assertEqual(req.wifi_min, 50)
        self.assertTrue(req.sockets)
        self.assertEqual(req.max_price, 50000)
        self.assertEqual(req.duration_hours, 3)

    def test_parse_free_query(self):
        parser = RuleBasedParser()
        req = parser.parse("bepul va Wi-Fi yaxshi joy kerak")
        self.assertEqual(req.max_price, 0)
        self.assertEqual(req.wifi_min, 20)

    def test_parse_unknown_district(self):
        parser = RuleBasedParser()
        req = parser.parse("qandaydir shaharda tinch joy")
        self.assertIsNone(req.district)
        self.assertEqual(req.noise, NoiseLevel.QUIET)


class MatchingTests(APITestCase):
    def setUp(self):
        self.district = District.objects.get_or_create(name="Chilonzor", defaults={"slug": "chilonzor"})[0]
        self.place = Place.objects.create(
            name="Quiet Coffee",
            district=self.district,
            address="a",
            latitude=41.27,
            longitude=69.21,
            price_per_hour=30000,
            wifi_speed=85,
            socket_count=8,
            noise_level=NoiseLevel.QUIET,
            available_slots=12,
            status=PlaceStatus.APPROVED,
        )
        self.other = Place.objects.create(
            name="Noisy Cafe",
            district=self.district,
            address="b",
            latitude=41.28,
            longitude=69.22,
            price_per_hour=60000,
            wifi_speed=5,
            socket_count=0,
            noise_level=NoiseLevel.NOISY,
            available_slots=0,
            status=PlaceStatus.APPROVED,
        )

    def _req(self, **kwargs):
        defaults = dict(district=None, noise=None, wifi_min=None, sockets=None, max_price=None, free_now=None)
        defaults.update(kwargs)
        return PlaceRequirements(**defaults)

    def test_match_filters_and_orders(self):
        req = self._req(district="chilonzor", noise=NoiseLevel.QUIET, wifi_min=50, sockets=True, max_price=50000)
        results = MatchingService.match(req)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["place"].name, "Quiet Coffee")
        self.assertEqual(results[0]["match_percent"], 100)

    def test_match_excludes_non_matching(self):
        req = self._req(district="chilonzor", noise=NoiseLevel.VERY_QUIET)
        results = MatchingService.match(req)
        self.assertEqual(len(results), 0)

    def test_match_no_requirements_returns_all(self):
        results = MatchingService.match(self._req())
        self.assertEqual(len(results), 2)

    def test_score_deterministic(self):
        req = self._req(noise=NoiseLevel.QUIET, wifi_min=50, sockets=True, max_price=30000)
        score1 = MatchingService.score(self.place, req)
        score2 = MatchingService.score(self.place, req)
        self.assertEqual(score1, score2)
        self.assertLessEqual(score1, 100)

    def test_score_higher_for_better_place(self):
        req = self._req(noise=NoiseLevel.QUIET, wifi_min=20, sockets=True, max_price=50000, free_now=True)
        best = MatchingService.score(self.place, req)
        worst = MatchingService.score(self.other, req)
        self.assertGreater(best, worst)


class AIChatAPITests(APITestCase):
    def setUp(self):
        District.objects.get_or_create(name="Chilonzor", defaults={"slug": "chilonzor"})[0]
        self.user = User.objects.create_user(email="ai@test.uz", password="AIPass123", full_name="AI")

    def test_chat_requires_message(self):
        resp = self.client.post("/api/ai/chat/", {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_chat_returns_results_from_db(self):
        district = District.objects.get(slug="chilonzor")
        Place.objects.create(
            name="Quiet Coffee",
            district=district,
            address="a",
            latitude=41.27,
            longitude=69.21,
            price_per_hour=30000,
            wifi_speed=85,
            socket_count=8,
            noise_level=NoiseLevel.QUIET,
            available_slots=12,
            status=PlaceStatus.APPROVED,
        )
        resp = self.client.post(
            "/api/ai/chat/",
            {"message": "Chilonzorda tinch, Wi-Fi tez, rozetkasi bor va 50 ming so'mdan arzon joy"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data["success"])
        self.assertGreaterEqual(len(resp.data["results"]), 1)
        self.assertEqual(resp.data["results"][0]["place"]["name"], "Quiet Coffee")
        self.assertLessEqual(resp.data["results"][0]["match_percent"], 100)

    def test_chat_empty_result(self):
        resp = self.client.post(
            "/api/ai/chat/", {"message": "Qo'qonda bepul joy"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["results"], [])

    def test_ai_status_endpoint(self):
        resp = self.client.get("/api/ai/status/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("ai_configured", resp.data)
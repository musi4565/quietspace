import json
import logging
import re

import httpx
from django.conf import settings

from apps.ai.services.requirements import PlaceRequirements
from apps.places.models import District, NoiseLevel

logger = logging.getLogger(__name__)


class BaseParser:
    """Foydalanuvchi matnini structured requirements ga aylantiradi."""

    def parse(self, text: str) -> PlaceRequirements:
        raise NotImplementedError


class RuleBasedParser(BaseParser):
    """AI kalitsiz ham ishlaydigan deterministik (keyword) parser."""

    NOISE_KEYWORDS = {
        "juda tinch": NoiseLevel.VERY_QUIET,
        "juda sokin": NoiseLevel.VERY_QUIET,
        "sokin": NoiseLevel.QUIET,
        "tinch": NoiseLevel.QUIET,
        "shovqinsiz": NoiseLevel.QUIET,
        "o'rtacha shovqin": NoiseLevel.AVERAGE,
        "ortacha shovqin": NoiseLevel.AVERAGE,
        "shovqinli": NoiseLevel.NOISY,
    }

    def __init__(self):
        self._districts = {}
        for d in District.objects.all():
            self._districts[d.name.lower()] = d.slug
            self._districts[d.slug.lower()] = d.slug

    def parse(self, text: str) -> PlaceRequirements:
        lowered = text.lower()

        req = PlaceRequirements(query_text=text)

        req.district = self._find_district(lowered)
        req.noise = self._find_noise(lowered)
        req.wifi_min = self._find_wifi(lowered)
        req.sockets = self._find_sockets(lowered)
        req.max_price = self._find_price(lowered)
        req.duration_hours = self._find_duration(lowered)
        req.free_now = self._find_free(lowered)

        return req

    def _find_district(self, text):
        for name, slug in self._districts.items():
            if name in text:
                return slug
        return None

    def _find_noise(self, text):
        for keyword, value in self.NOISE_KEYWORDS.items():
            if keyword in text:
                return value
        return None

    def _find_wifi(self, text):
        if re.search(r"wi-?fi\s*(juda\s*)?tez", text) or re.search(r"internet\s*(juda\s*)?tez", text):
            return 50
        if re.search(r"wi-?fi\s*yaxshi", text) or re.search(r"internet\s*yaxshi", text):
            return 20
        return None

    def _find_sockets(self, text):
        if re.search(r"rozetka|quvvat|toki\s*bor|toki\s*bormi", text):
            return True
        return None

    def _find_price(self, text):
        if re.search(r"\bbepul\b", text):
            return 0
        match = re.search(r"(\d+)\s*(ming|k)?\s*so'?m", text)
        if match:
            number = int(match.group(1))
            unit = match.group(2)
            if unit:
                return number * 1000
            if number < 1000:
                return number * 1000
            return number
        return None

    def _find_duration(self, text):
        match = re.search(r"(\d+)\s*soat", text)
        if match:
            return int(match.group(1))
        return None

    def _find_free(self, text):
        if re.search(r"hozir\s*bo'?sh|joy\s*(bor|bormi)|bo'?sh\s*joy", text):
            return True
        return None


SYSTEM_PROMPT = (
    "Siz QuietSpace Tashkent AI assistantisiz. Foydalanuvchi ishlash/o'qish uchun "
    "joy qidirish talabini yozadi. Siz faqat JSON qaytarasiz, boshqa hech narsa yo'q. "
    "JSON kalitlari: district (Toshkent tumani slug'i yoki null), noise "
    "(VERY_QUIET|QUIET|AVERAGE|NOISY yoki null), wifi_min (son yoki null), "
    "sockets (true/false/null), max_price (so'mda son yoki null), "
    "duration_hours (soat son yoki null), free_now (true/false/null). "
    "Noma'lum bo'lsa null qo'ying. Narsalarni o'ylab topmang. "
    "Narx misollari: 'bepul' -> max_price: 0; '50 mingdan arzon' -> max_price: 50000; "
    "'100 minggacha' -> max_price: 100000. "
    "Wi-Fi misollari: 'wi-fi yaxshi' -> wifi_min: 20; 'wi-fi tez' -> wifi_min: 50. "
    "Tuman slug misollari: 'chilonzor', 'yunusobod', 'shayxontohur' (slash yoki nomi bo'lsa slug'ga aylantiring).\n"
    "To'liq misol: 'Menga Chilonzorda 50 mingdan arzon, tinch va Wi-Fi yaxshi joy kerak' "
    "-> {\"district\": \"chilonzor\", \"noise\": \"QUIET\", \"wifi_min\": 20, "
    "\"sockets\": null, \"max_price\": 50000, \"duration_hours\": null, \"free_now\": null}"
)


def normalize_requirements(data: dict) -> PlaceRequirements:
    """LLM dan kelgan JSON'ni PlaceRequirements ga o'tkazadi. Maydonlarni o'ylab topmaydi -
    faqat DB dagi tumanlar va qoidalarga mos bo'lganlarini qabul qiladi."""
    req = PlaceRequirements()

    district = data.get("district")
    if district:
        district_obj = (
            District.objects.filter(slug__iexact=str(district).lower()).first()
            or District.objects.filter(name__iexact=str(district)).first()
        )
        req.district = district_obj.slug if district_obj else None

    noise = str(data.get("noise") or "").upper()
    if noise in NoiseLevel.values:
        req.noise = noise

    wifi = data.get("wifi_min")
    if wifi is not None and int(wifi) > 0:
        req.wifi_min = int(wifi)

    sockets = data.get("sockets")
    if sockets is not None:
        req.sockets = bool(sockets)

    price = data.get("max_price")
    if price is not None and int(price) >= 0:
        req.max_price = int(price)

    duration = data.get("duration_hours")
    if duration is not None and int(duration) > 0:
        req.duration_hours = int(duration)

    free = data.get("free_now")
    if free is not None:
        req.free_now = bool(free)

    return req


class OpenAICompatParser(BaseParser):
    """AI provider (OpenAI-compatible API) orqali parsing."""

    def __init__(self):
        self.api_key = settings.AI_API_KEY
        self.base_url = settings.AI_BASE_URL.rstrip("/")
        self.model = settings.AI_MODEL
        self._fallback = RuleBasedParser()

    def parse(self, text: str) -> PlaceRequirements:
        try:
            result = self._call_api(text)
            req = normalize_requirements(result)
            req.query_text = text
            return req
        except Exception as exc:
            logger.warning("AI parser xatosi, rule-based ga o'tilmoqda: %s", exc)
            return self._fallback.parse(text)

    def _call_api(self, text: str) -> dict:
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={
                "model": self.model,
                "temperature": 0,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
            },
            timeout=15,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[-1]
            content = content.rsplit("```", 1)[0]
        return json.loads(content)


class GeminiParser(BaseParser):
    """Google Gemini (generativelanguage API) orqali parsing. JSON mode ishlatadi."""

    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        self._fallback = RuleBasedParser()

    def parse(self, text: str) -> PlaceRequirements:
        try:
            result = self._call_api(text)
            req = normalize_requirements(result)
            req.query_text = text
            return req
        except Exception as exc:
            logger.warning("Gemini parser xatosi, rule-based ga o'tilmoqda: %s", exc)
            return self._fallback.parse(text)

    def _call_api(self, text: str) -> dict:
        response = httpx.post(
            self.API_URL.format(model=self.model),
            params={"key": self.api_key},
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": text}]}],
                "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                "generationConfig": {"temperature": 0, "responseMimeType": "application/json"},
            },
            timeout=15,
        )
        response.raise_for_status()
        content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(content.strip())


def get_parser() -> BaseParser:
    """Konfiguratsiyaga qarab parser tanlaydi: Gemini > OpenAI > rule-based."""
    if settings.GEMINI_API_KEY:
        return GeminiParser()
    if settings.AI_API_KEY:
        return OpenAICompatParser()
    return RuleBasedParser()


class GeminiParser(BaseParser):
    """Google Gemini (generativelanguage API) orqali parsing. JSON mode ishlatadi."""

    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        self._fallback = RuleBasedParser()

    def parse(self, text: str) -> PlaceRequirements:
        try:
            result = self._call_api(text)
            req = normalize_requirements(result)
            req.query_text = text
            return req
        except Exception as exc:
            logger.warning("Gemini parser xatosi, rule-based ga o'tilmoqda: %s", exc)
            return self._fallback.parse(text)

    def _call_api(self, text: str) -> dict:
        response = httpx.post(
            self.API_URL.format(model=self.model),
            params={"key": self.api_key},
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": text}]}],
                "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                "generationConfig": {"temperature": 0, "responseMimeType": "application/json"},
            },
            timeout=15,
        )
        response.raise_for_status()
        content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(content.strip())


def get_parser() -> BaseParser:
    """Konfiguratsiyaga qarab parser tanlaydi: Gemini > OpenAI > rule-based."""
    if settings.GEMINI_API_KEY:
        return GeminiParser()
    if settings.AI_API_KEY:
        return OpenAICompatParser()
    return RuleBasedParser()
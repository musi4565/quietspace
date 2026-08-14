from django.db.models import Avg, Count, Q

from apps.ai.services.requirements import PlaceRequirements
from apps.places.models import NoiseLevel, Place, PlaceStatus

# Deterministik scoring vaznlari (jami 100)
WEIGHTS = {
    "noise": 30,
    "wifi": 25,
    "sockets": 20,
    "price": 15,
    "distance": 10,
}

NOISE_ORDER = [NoiseLevel.VERY_QUIET, NoiseLevel.QUIET, NoiseLevel.AVERAGE, NoiseLevel.NOISY]


class MatchingService:
    """Talablar asosida PostgreSQL'dan joylarni topib, aniq ball beradi.

    AI hech narsani o'ylab topmaydi: faqat shu queryset ichidagi joylar qaytadi.
    """

    @staticmethod
    def build_queryset(req: PlaceRequirements):
        qs = (
            Place.objects.filter(status=PlaceStatus.APPROVED)
            .select_related("district")
            .prefetch_related("images")
            .annotate(avg_rating=Avg("reviews__rating"), rating_count=Count("reviews"))
        )

        if req.district:
            qs = qs.filter(district__slug=req.district)

        if req.max_price is not None:
            qs = qs.filter(price_per_hour__lte=req.max_price)

        if req.wifi_min:
            qs = qs.filter(wifi_speed__gte=req.wifi_min)

        if req.sockets:
            qs = qs.filter(socket_count__gt=0)

        if req.noise:
            allowed = NOISE_ORDER[: NOISE_ORDER.index(req.noise) + 1]
            qs = qs.filter(noise_level__in=allowed)

        if req.free_now:
            qs = qs.filter(available_slots__gt=0)

        return qs

    @staticmethod
    def score(place: Place, req: PlaceRequirements) -> int:
        total = 0

        if req.noise:
            place_idx = NOISE_ORDER.index(place.noise_level)
            req_idx = NOISE_ORDER.index(req.noise)
            if place_idx <= req_idx:
                total += WEIGHTS["noise"]
            elif place_idx == req_idx + 1:
                total += 20
            elif place_idx == req_idx + 2:
                total += 10
            else:
                total += 0
        else:
            total += WEIGHTS["noise"]

        if req.wifi_min:
            total += min(WEIGHTS["wifi"], round(WEIGHTS["wifi"] * place.wifi_speed / req.wifi_min))
        else:
            total += WEIGHTS["wifi"]

        if req.sockets:
            total += WEIGHTS["sockets"] if place.socket_count > 0 else 0
        else:
            total += WEIGHTS["sockets"]

        if req.max_price is not None:
            if place.price_per_hour <= req.max_price:
                total += WEIGHTS["price"]
            elif req.max_price > 0:
                total += min(WEIGHTS["price"], round(WEIGHTS["price"] * req.max_price / place.price_per_hour))
            else:
                total += 0
        else:
            total += WEIGHTS["price"]

        # Masofa so'ralmagan -> neytral ball (adolatli taqsimot)
        total += WEIGHTS["distance"]

        return min(100, total)

    @classmethod
    def match(cls, req: PlaceRequirements, limit: int = 10):
        qs = cls.build_queryset(req)
        scored = []
        for place in qs[:200]:
            scored.append({"place": place, "match_percent": cls.score(place, req)})
        scored.sort(key=lambda item: item["match_percent"], reverse=True)
        return scored[:limit]
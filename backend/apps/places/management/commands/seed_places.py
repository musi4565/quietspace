import io
import secrets  # noqa: F401

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw

from apps.accounts.models import Role, User
from apps.places.models import District, NoiseLevel, Place, PlaceImage, PlaceStatus

SEED_PLACES = [
    {
        "name": "Quiet Coffee",
        "district": "Chilonzor",
        "address": "Chilonzor 9-kvartal, 12-uy",
        "lat": 41.2744, "lon": 69.2160,
        "price": 30000, "wifi": 85, "sockets": 8, "noise": "QUIET",
        "capacity": 30, "slots": 12,
        "description": "Yashil maydon yaqinidagi sokin kofexona. Katta stollar, yaxshi yorug'lik va barqaror internet. Ish uchun juda mos.",
        "featured": True,
    },
    {
        "name": "WorkHub Tashkent",
        "district": "Yunusobod",
        "address": "Amir Temur ko'chasi 107B",
        "lat": 41.3240, "lon": 69.2690,
        "price": 45000, "wifi": 100, "sockets": 25, "noise": "QUIET",
        "capacity": 80, "slots": 20,
        "description": "Professional coworking: alohida xonalar, printer, qahva mashinasi, 24/7 kirish.",
        "featured": True,
    },
    {
        "name": "Library Zone",
        "district": "Mirzo Ulug'bek",
        "address": "Buyuk Ipak Yo'li ko'chasi 89",
        "lat": 41.3370, "lon": 69.3050,
        "price": 0, "wifi": 40, "sockets": 4, "noise": "VERY_QUIET",
        "capacity": 50, "slots": 8,
        "description": "Shahar kutubxonasi — mutlaqo tinch, bepul. Rozetkalar cheklangan, shuning uchun erta kelish tavsiya etiladi.",
        "featured": False,
    },
    {
        "name": "Green Garden Cafe",
        "district": "Yakkasaroy",
        "address": "Kichik Beshyagach ko'chasi 5",
        "lat": 41.2920, "lon": 69.2600,
        "price": 25000, "wifi": 55, "sockets": 6, "noise": "AVERAGE",
        "capacity": 25, "slots": 3,
        "description": "Bog'li kafe, ochiq havo zonasi. Kun davomida nisbatan tinch, kechqurun jonli.",
        "featured": False,
    },
    {
        "name": "Focus Point Coworking",
        "district": "Shayxontohur",
        "address": "Navoiy ko'chasi 18",
        "lat": 41.3100, "lon": 69.2450,
        "price": 60000, "wifi": 120, "sockets": 30, "noise": "VERY_QUIET",
        "capacity": 60, "slots": 0,
        "description": "Premium coworking — ovoz izolyatsiyasi, alohida kabinetlar. Hozir joylar to'liq.",
        "featured": True,
    },
    {
        "name": "Sergeli Library",
        "district": "Sergeli",
        "address": "Sergeli-4, 12-mavze",
        "lat": 41.2390, "lon": 69.1960,
        "price": 0, "wifi": 30, "sockets": 2, "noise": "VERY_QUIET",
        "capacity": 40, "slots": 15,
        "description": "Bepul kutubxona, tinch muhit. Wi-Fi o'rtacha darajada.",
        "featured": False,
    },
    {
        "name": "Cozy Corner",
        "district": "Olmazor",
        "address": "Farobiy ko'chasi 6",
        "lat": 41.2600, "lon": 69.2300,
        "price": 20000, "wifi": 45, "sockets": 5, "noise": "QUIET",
        "capacity": 20, "slots": 6,
        "description": "Kichik va shinam kafe. Issiq ichimliklar, barqaror internet.",
        "featured": False,
    },
    {
        "name": "Uchtepa Cowork",
        "district": "Uchtepa",
        "address": "Chilonzor ko'chasi 1A",
        "lat": 41.2760, "lon": 69.1820,
        "price": 35000, "wifi": 70, "sockets": 15, "noise": "AVERAGE",
        "capacity": 45, "slots": 10,
        "description": "Arzon coworking — 24/7 ishlaydi, kichik meeting xonasi bor.",
        "featured": False,
    },
    {
        "name": "Bukhara Teahouse",
        "district": "Mirobod",
        "address": "Nukus ko'chasi 41",
        "lat": 41.2900, "lon": 69.2850,
        "price": 15000, "wifi": 25, "sockets": 3, "noise": "NOISY",
        "capacity": 35, "slots": 5,
        "description": "Milliy choyxona — muloqot uchun, ish uchun emas. Shovqin darajasi yuqori.",
        "featured": False,
    },
    {
        "name": "Silk Road Hub",
        "district": "Bektemir",
        "address": "Qoraqamish ko'chasi 22",
        "lat": 41.2350, "lon": 69.3300,
        "price": 50000, "wifi": 90, "sockets": 20, "noise": "QUIET",
        "capacity": 55, "slots": 18,
        "description": "Yangi coworking — hammasi yangi, toza havo va shahar shovqinidan uzoqda.",
        "featured": True,
    },
    {
        "name": "Yangihayot Garden",
        "district": "Yangihayot",
        "address": "Temur Malik ko'chasi 3",
        "lat": 41.2630, "lon": 69.1800,
        "price": 10000, "wifi": 35, "sockets": 4, "noise": "AVERAGE",
        "capacity": 30, "slots": 9,
        "description": "Bog'oldi kafesi, ochiq havo. Uyga yaqin, arzon narx.",
        "featured": False,
    },
    {
        "name": "Yashnobod Study Room",
        "district": "Yashnobod",
        "address": "Maxtumquli ko'chasi 14",
        "lat": 41.2930, "lon": 69.3150,
        "price": 0, "wifi": 20, "sockets": 6, "noise": "VERY_QUIET",
        "capacity": 25, "slots": 4,
        "description": "O'quv xonasi — talabalar uchun bepul. Tinch va tartibli.",
        "featured": False,
    },
]


def make_placeholder_image(color, text):
    img = Image.new("RGB", (800, 500), color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 790, 490], outline=(255, 255, 255), width=2)
    draw.text((60, 220), text, fill=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return ContentFile(buf.getvalue(), name=f"{text.replace(' ', '_').lower()}.png")


COLORS = ["#2E7D64", "#3A7CA5", "#5C6BC0", "#8D6E63", "#455A64", "#7B6C1E"]


class Command(BaseCommand):
    help = "Development uchun namunaviy joylar yaratadi (APPROVED)."

    def handle(self, *args, **options):
        owner, created = User.objects.get_or_create(
            email="owner@quietspace.uz",
            defaults={"full_name": "Demo Owner", "role": Role.PLACE_OWNER},
        )
        if created:
            owner.set_password("ownerpass123")
            owner.save()

        count = 0
        for idx, data in enumerate(SEED_PLACES):
            district = District.objects.get(name=data["district"])
            place, created = Place.objects.get_or_create(
                name=data["name"],
                defaults={
                    "district": district,
                    "address": data["address"],
                    "latitude": data["lat"],
                    "longitude": data["lon"],
                    "price_per_hour": data["price"],
                    "wifi_speed": data["wifi"],
                    "socket_count": data["sockets"],
                    "noise_level": data["noise"],
                    "capacity": data["capacity"],
                    "available_slots": data["slots"],
                    "description": data["description"],
                    "status": PlaceStatus.APPROVED,
                    "is_featured": data["featured"],
                    "owner": owner,
                },
            )
            if created:
                image = make_placeholder_image(COLORS[idx % len(COLORS)], place.name)
                PlaceImage.objects.create(place=place, image=image, is_primary=True)
                count += 1

        self.stdout.write(self.style.SUCCESS(f"{count} ta namunaviy joy yaratildi."))
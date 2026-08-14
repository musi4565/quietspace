from django.db import migrations

DISTRICTS = [
    "Chilonzor", "Yunusobod", "Yakkasaroy", "Mirzo Ulug'bek", "Shayxontohur",
    "Olmazor", "Uchtepa", "Bektemir", "Mirobod", "Sergeli", "Yashnobod",
    "Yangihayot",
]


def seed_districts(apps, schema_editor):
    District = apps.get_model("places", "District")
    for name in DISTRICTS:
        slug = name.lower().replace(" ", "-").replace("'", "")
        District.objects.get_or_create(name=name, defaults={"slug": slug})


def unseed_districts(apps, schema_editor):
    District = apps.get_model("places", "District")
    District.objects.filter(name__in=DISTRICTS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("places", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_districts, unseed_districts),
    ]
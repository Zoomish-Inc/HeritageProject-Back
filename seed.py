import os
import django
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from heritage.models import HeritageObject

HeritageObject.objects.all().delete()
print("База очищена.")

# Ручные slug-и
slugs = {
    "Медресе Кукельдаш": "kukeldash-madrasa",
    "Мавзолей Шейха Зайнуддина": "shaykh-zaynuddin-mausoleum",
    "Дворец Ташкентского хана": "tashkent-khan-palace",
    "Минарет Калян": "kalyan-minaret",
    "Арк Бухары": "ark-of-bukhara",
    "Регистан Самарканда": "registan-square",
}

data = [
    {"name_ru": "Медресе Кукельдаш", "name_uz": "Koʻkeldosh madrasasi", "year_built": 1569, "address_ru": "Ташкент, старый город", "short_description_ru": "Одно из самых крупных медресе в Центральной Азии.", "order": 1},
    {"name_ru": "Мавзолей Шейха Зайнуддина", "name_uz": "Shayx Zayniddin maqbarasi", "year_built": 1556, "address_ru": "Ташкент, Шайхантахур", "short_description_ru": "Выдающийся памятник XVI века.", "order": 2},
    {"name_ru": "Дворец Ташкентского хана", "name_uz": "Toshkent xoni saroyi", "year_built": 1800, "address_ru": "Ташкент, центр", "short_description_ru": "Резиденция кокандских ханов.", "order": 3},
    {"name_ru": "Минарет Калян", "name_uz": "Kalyon minorasi", "year_built": 1127, "address_ru": "Бухара", "short_description_ru": "Знаменитый минарет высотой 47 метров.", "order": 4},
    {"name_ru": "Арк Бухары", "name_uz": "Buxoro arki", "year_built": 500, "address_ru": "Бухара", "short_description_ru": "Древняя цитадель Бухары.", "order": 5},
    {"name_ru": "Регистан Самарканда", "name_uz": "Registon maydoni", "year_built": 1420, "address_ru": "Самарканд", "short_description_ru": "Жемчужина тимуридской архитектуры.", "order": 6},
]

for item in data:
    slug = slugs[item["name_ru"]]  # берём из словаря
    obj = HeritageObject.objects.create(
        name_ru=item["name_ru"],
        name_uz=item.get("name_uz", ""),
        year_built=item.get("year_built"),
        address_ru=item.get("address_ru", ""),
        short_description_ru=item.get("short_description_ru", ""),
        order=item["order"],
        is_published=True,
        slug=slug,
        cover_image=f"https://picsum.photos/id/{100 + item['order']}/800/600"
    )
    print(f"✅ {obj.order}. {obj.name_ru} (slug: {obj.slug})")

print("\n🎉 Успешно создано 6 объектов!")
print("Всего опубликованных:", HeritageObject.objects.filter(is_published=True).count())
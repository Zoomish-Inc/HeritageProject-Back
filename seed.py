import os
import django
from django.utils.text import slugify

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from heritage.models import HeritageObject


def seed_heritage():
    """Создаёт ровно 6 опубликованных объектов согласно ТЗ"""

    # Очищаем предыдущие данные
    HeritageObject.objects.all().delete()

    data = [
        {
            "slug": "zdanie-voennogo-sobraniya-dom-oficerov",
            "name_ru": "Здание военного собрания (Дом офицеров)",
            "name_uz": "Harbiylar uyi",
            "address_ru": "Ташкент, ул. Амира Темура",
            "address_uz": "Toshkent, Amir Temur koʻchasi",
            "shortDescription_ru": "Одно из красивейших зданий колониального Ташкента.",
            "shortDescription_uz": "Toshkentning eng go'zal binolaridan biri.",
            "yearBuilt": 1900,
            "order": 1,
            "coverImageUrl": "https://picsum.photos/id/1015/800/600",
        },
        {
            "slug": "gubernatorskiy-dom",
            "name_ru": "Губернаторский дом",
            "name_uz": "Gubernator uyi",
            "address_ru": "Ташкент, Сквер Амира Темура",
            "address_uz": "Toshkent, Amir Temur maydoni",
            "shortDescription_ru": "Резиденция генерал-губернатора Туркестанского края.",
            "shortDescription_uz": "Turkiston oʻlkasi general-gubernatori qarorgohi.",
            "yearBuilt": 1890,
            "order": 2,
            "coverImageUrl": "https://picsum.photos/id/102/800/600",
        },
        {
            "slug": "zhenskaya-gimnaziya",
            "name_ru": "Женская гимназия",
            "name_uz": "Qizlar gimnaziyasi",
            "address_ru": "Ташкент, центр",
            "address_uz": "Toshkent, markaz",
            "shortDescription_ru": "Первая женская гимназия в Туркестане.",
            "shortDescription_uz": "Turkistondagi birinchi qizlar gimnaziyasi.",
            "yearBuilt": 1880,
            "order": 3,
            "coverImageUrl": "https://picsum.photos/id/133/800/600",
        },
        {
            "slug": "chasovnya-aleksandra-nevskogo",
            "name_ru": "Часовня Александра Невского",
            "name_uz": "Aleksandr Nevskiy ibodatxonasi",
            "address_ru": "Ташкент, старый город",
            "address_uz": "Toshkent, eski shahar",
            "shortDescription_ru": "Памятник русско-туркестанской истории.",
            "shortDescription_uz": "Rus-Turkiston tarixiy yodgorligi.",
            "yearBuilt": 1890,
            "order": 4,
            "coverImageUrl": "https://picsum.photos/id/201/800/600",
        },
        {
            "slug": "khram-sergiya-radonezhskogo",
            "name_ru": "Храм Сергия Радонежского",
            "name_uz": "Sergiy Radonejskiy cherkovi",
            "address_ru": "Ташкент",
            "address_uz": "Toshkent",
            "shortDescription_ru": "Православный храм в Ташкенте.",
            "shortDescription_uz": "Toshkentdagi pravoslav cherkovi.",
            "yearBuilt": 1940,
            "order": 5,
            "coverImageUrl": "https://picsum.photos/id/251/800/600",
        },
        {
            "slug": "muzhskaya-gimnaziya",
            "name_ru": "Мужская гимназия",
            "name_uz": "O'g'il bolalar gimnaziyasi",
            "address_ru": "Ташкент, центр",
            "address_uz": "Toshkent, markaz",
            "shortDescription_ru": "Одно из старейших учебных заведений региона.",
            "shortDescription_uz": "Mintaqadagi eng qadimgi o'quv yurtlaridan biri.",
            "yearBuilt": 1870,
            "order": 6,
            "coverImageUrl": "https://picsum.photos/id/180/800/600",
        },
    ]

    for item in data:
        obj = HeritageObject.objects.create(
            slug=item["slug"],
            name_ru=item["name_ru"],
            name_uz=item.get("name_uz", ""),
            address_ru=item["address_ru"],
            address_uz=item.get("address_uz", ""),
            shortDescription_ru=item["shortDescription_ru"],
            shortDescription_uz=item.get("shortDescription_uz", ""),
            yearBuilt=item.get("yearBuilt"),
            order=item["order"],
            isPublished=True,
            coverImageUrl=item["coverImageUrl"],
        )
        print(f"✅ {obj.order}. {obj.name_ru} (slug: {obj.slug})")

    print("\n🎉 Успешно создано ровно 6 опубликованных объектов!")


if __name__ == "__main__":
    seed_heritage()
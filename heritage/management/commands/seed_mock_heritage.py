import json
import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from heritage.models import (
    ArchitectBio,
    ArchitectureDetail,
    AudioGuide,
    AudioGuideTrack,
    BeforeAfterPair,
    BiographyMilestone,
    HeritageObject,
    HistoricalFigure,
    PhotoItem,
)
from media_files.models import MediaFile

DATA_PATH = Path(__file__).resolve().parents[2] / 'data' / 'mock_heritage_objects.json'
KNOWN_SLUGS = [
    'zhenskaya-gimnaziya',
    'khram-sergiya-radonezhskogo',
    'chasovnya-aleksandra-nevskogo',
    'zdanie-voennogo-sobraniya-dom-oficerov',
    'gubernatorskiy-dom',
    'muzhskaya-gimnaziya',
]


def loc(value, default=None):
    if not value:
        return default or {'ru': '', 'uz': ''}
    return {
        'ru': value.get('ru') or '',
        'uz': value.get('uz') or '',
    }


def char255(value):
    return (value or '')[:255]


def resolve_url(url, frontend_base):
    if not url:
        return ''
    if url.startswith('http://') or url.startswith('https://'):
        return url
    if url.startswith('/'):
        return f'{frontend_base.rstrip("/")}{url}'
    return url


def parse_uuid(value):
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError, AttributeError):
        return None


def create_media_file(title_ru, url, frontend_base, media_type='image', caption=None):
    absolute_url = resolve_url(url, frontend_base)
    caption = caption or {}
    return MediaFile.objects.create(
        title_ru=char255(title_ru or 'Media'),
        title_uz=char255(caption.get('uz') or title_ru or 'Media'),
        file=ContentFile(b'', name='remote-placeholder.jpg'),
        media_type=media_type,
        caption_ru=caption.get('ru') or '',
        caption_uz=caption.get('uz') or '',
        source=absolute_url,
    )


def create_milestones(items):
    milestones = []
    for index, item in enumerate(items or []):
        event = loc(item.get('event'))
        milestones.append(
            BiographyMilestone.objects.create(
                year=item.get('year') or 0,
                event_ru=char255(event['ru']),
                event_uz=char255(event['uz']),
                order=index,
            )
        )
    return milestones


class Command(BaseCommand):
    help = 'Seed HeritageObject records from frontend mock data.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Delete existing mock heritage objects and re-import.',
        )

    def handle(self, *args, **options):
        if not DATA_PATH.exists():
            self.stderr.write(self.style.ERROR(f'Mock data file not found: {DATA_PATH}'))
            return

        with DATA_PATH.open(encoding='utf-8') as handle:
            items = json.load(handle)

        existing = HeritageObject.objects.filter(slug__in=KNOWN_SLUGS).count()
        if existing >= len(KNOWN_SLUGS) and not options['force']:
            self.stdout.write(self.style.WARNING('Mock heritage data already present, skipping.'))
            return

        if options['force']:
            HeritageObject.objects.filter(slug__in=KNOWN_SLUGS).delete()

        frontend_base = getattr(
            settings,
            'FRONTEND_BASE_URL',
            'https://heritage-project-front.vercel.app',
        )

        for item in items:
            slug = item['slug']
            with transaction.atomic():
                imported = self._import_object(item, frontend_base)
            if imported:
                self.stdout.write(f'Imported: {slug}')

        self.stdout.write(self.style.SUCCESS(f'Seeded {len(items)} heritage objects.'))

    def _import_object(self, item, frontend_base):
        slug = item['slug']
        if HeritageObject.objects.filter(slug=slug).exists():
            self.stdout.write(f'Skip existing slug: {slug}')
            return False

        name = loc(item.get('name'))
        former_name = loc(item.get('formerName'))
        current_purpose = loc(item.get('currentPurpose'))
        historical_purpose = loc(item.get('historicalPurpose'))
        address = loc(item.get('address'))
        year_label = loc(item.get('yearBuiltLabel'))
        style = loc(item.get('architecturalStyle'))
        architect = loc(item.get('architect'))
        short_description = loc(item.get('shortDescription'))
        architectural_description = loc(item.get('architecturalDescription'))
        history = loc(item.get('history'))
        coordinates = item.get('coordinates') or {}

        obj = HeritageObject.objects.create(
            id=parse_uuid(item.get('id')) or uuid.uuid4(),
            slug=slug,
            order=item.get('order') or 0,
            name_ru=char255(name['ru']),
            name_uz=char255(name['uz']),
            formerName_ru=char255(former_name['ru']),
            formerName_uz=char255(former_name['uz']),
            currentPurpose_ru=char255(current_purpose['ru']),
            currentPurpose_uz=char255(current_purpose['uz']),
            historicalPurpose_ru=char255(historical_purpose['ru']),
            historicalPurpose_uz=char255(historical_purpose['uz']),
            address_ru=address['ru'],
            address_uz=address['uz'],
            lat=coordinates.get('lat'),
            lng=coordinates.get('lng'),
            mapUrl=item.get('mapUrl') or '',
            yearBuilt=item.get('yearBuilt'),
            yearRange=str(item.get('yearBuilt') or '')[:50],
            yearBuiltLabel_ru=char255(year_label['ru']),
            yearBuiltLabel_uz=char255(year_label['uz']),
            architecturalStyle_ru=char255(style['ru']),
            architecturalStyle_uz=char255(style['uz']),
            architect_ru=char255(architect['ru']),
            architect_uz=char255(architect['uz']),
            shortDescription_ru=short_description['ru'],
            shortDescription_uz=short_description['uz'],
            architecturalDescription_ru=architectural_description['ru'],
            architecturalDescription_uz=architectural_description['uz'],
            history_ru=history['ru'],
            history_uz=history['uz'],
            coverImageUrl=resolve_url(item.get('coverImageUrl'), frontend_base),
            isPublished=True,
            tourPublished=False,
        )

        for index, detail in enumerate(item.get('architectureDetails') or []):
            title = loc(detail.get('title'))
            description = loc(detail.get('description'))
            ArchitectureDetail.objects.create(
                heritage=obj,
                title_ru=char255(title['ru']),
                title_uz=char255(title['uz']),
                description_ru=description['ru'],
                description_uz=description['uz'],
                imageUrl=resolve_url(detail.get('imageUrl'), frontend_base),
                order=index,
            )

        for index, photo in enumerate(item.get('photos') or []):
            caption = loc(photo.get('caption'))
            PhotoItem.objects.create(
                heritage=obj,
                url=resolve_url(photo.get('url'), frontend_base),
                caption_ru=char255(caption['ru']),
                caption_uz=char255(caption['uz']),
                sourceUrl=photo.get('sourceUrl') or '',
                isHistorical=False,
                year=photo.get('year') or 0,
                order=index,
            )

        for index, media in enumerate(item.get('historyMedia') or []):
            caption = loc(media.get('caption'))
            PhotoItem.objects.create(
                heritage=obj,
                heritage_history_media=obj,
                url=resolve_url(media.get('url'), frontend_base),
                caption_ru=char255(caption['ru']),
                caption_uz=char255(caption['uz']),
                sourceUrl=media.get('sourceUrl') or '',
                isHistorical=True,
                year=media.get('year') or 0,
                order=index,
            )

        for index, figure in enumerate(item.get('historicalFigures') or []):
            name_f = loc(figure.get('name'))
            role = loc(figure.get('role'))
            bio = loc(figure.get('bio'))
            credit = loc(figure.get('bioSourceCredit'))
            historical = HistoricalFigure.objects.create(
                heritage=obj,
                name_ru=char255(name_f['ru']),
                name_uz=char255(name_f['uz']),
                role_ru=char255(role['ru']),
                role_uz=char255(role['uz']),
                bio_ru=bio['ru'],
                bio_uz=bio['uz'],
                photoUrl=resolve_url(figure.get('photoUrl'), frontend_base),
                bioSourceUrl=figure.get('bioSourceUrl') or '',
                bioSourceCredit_ru=char255(credit['ru']),
                bioSourceCredit_uz=char255(credit['uz']),
                order=index,
            )
            milestones = create_milestones(figure.get('milestones'))
            if milestones:
                historical.milestones.set(milestones)

        architect_bio = item.get('architectBio')
        if architect_bio:
            name_a = loc(architect_bio.get('name'))
            role_a = loc(architect_bio.get('role'))
            bio_a = loc(architect_bio.get('bio'))
            bio_obj = ArchitectBio.objects.create(
                heritage=obj,
                name_ru=char255(name_a['ru']),
                name_uz=char255(name_a['uz']),
                role_ru=char255(role_a['ru']),
                role_uz=char255(role_a['uz']),
                bio_ru=bio_a['ru'],
                bio_uz=bio_a['uz'],
                photoUrl=resolve_url(architect_bio.get('photoUrl'), frontend_base),
            )
            milestones = create_milestones(architect_bio.get('milestones'))
            if milestones:
                bio_obj.milestones.set(milestones)

        for index, pair in enumerate(item.get('beforeAfterPairs') or []):
            label = loc(pair.get('label'))
            before = pair.get('before') or {}
            after = pair.get('after') or {}
            before_media = create_media_file(
                label['ru'] or obj.name_ru,
                before.get('url'),
                frontend_base,
                caption=before.get('caption'),
            )
            after_media = create_media_file(
                label['ru'] or obj.name_ru,
                after.get('url'),
                frontend_base,
                caption=after.get('caption'),
            )
            if after.get('sourceUrl'):
                after_media.source = after['sourceUrl']
                after_media.save(update_fields=['source'])
            BeforeAfterPair.objects.create(
                heritage_object=obj,
                label_ru=char255(label['ru']),
                label_uz=char255(label['uz']),
                before=before_media,
                after=after_media,
                year_before=pair.get('year_before'),
                year_after=pair.get('year_after'),
                sort_order=index,
            )

        audio = item.get('audioGuide')
        if audio and (audio.get('tracks') or any(
            loc(audio.get(key))['ru'] or loc(audio.get(key))['uz']
            for key in ('narratorLabel', 'transcript', 'atmosphereDescription', 'musicSuggestion')
        )):
            narrator = loc(audio.get('narratorLabel'))
            transcript = loc(audio.get('transcript'))
            atmosphere = loc(audio.get('atmosphereDescription'))
            music = loc(audio.get('musicSuggestion'))
            guide = AudioGuide.objects.create(
                heritage=obj,
                narratorLabel_ru=char255(narrator['ru']),
                narratorLabel_uz=char255(narrator['uz']),
                transcript_ru=transcript['ru'],
                transcript_uz=transcript['uz'],
                atmosphereDescription_ru=atmosphere['ru'],
                atmosphereDescription_uz=atmosphere['uz'],
                musicSuggestion_ru=music['ru'],
                musicSuggestion_uz=music['uz'],
            )
            for index, track in enumerate(audio.get('tracks') or []):
                short_title = loc(track.get('shortTitle'))
                full_title = loc(track.get('fullTitle'))
                AudioGuideTrack.objects.create(
                    audio_guide=guide,
                    url=resolve_url(track.get('url'), frontend_base),
                    shortTitle_ru=char255(short_title['ru']),
                    shortTitle_uz=char255(short_title['uz']),
                    fullTitle_ru=char255(full_title['ru']),
                    fullTitle_uz=char255(full_title['uz']),
                    order=index,
                )

        return True

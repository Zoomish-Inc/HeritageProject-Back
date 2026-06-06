from django.db.models.signals import m2m_changed, post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from . import cache_service
from .models import (
    ArchitectBio,
    ArchitectureDetail,
    AudioGuide,
    AudioGuideTrack,
    BeforeAfterPair,
    HeritageObject,
    HistoricalFigure,
    PhotoItem,
)
from .tour_packs import tour_fields_changed, trigger_vercel_deploy


def _invalidate_by_slug(slug):
    if slug:
        cache_service.invalidate_heritage(slug=slug)


def _heritage_slug_from_instance(instance):
    if isinstance(instance, HeritageObject):
        return instance.slug
    if isinstance(instance, BeforeAfterPair):
        return instance.heritage_object.slug if instance.heritage_object_id else None
    if isinstance(instance, AudioGuideTrack):
        if instance.audio_guide_id and instance.audio_guide.heritage_id:
            return instance.audio_guide.heritage.slug
        return None
    heritage = getattr(instance, 'heritage', None)
    if heritage is not None:
        return heritage.slug
    return None


@receiver(pre_save, sender=HeritageObject)
def heritage_object_pre_save(sender, instance, **kwargs):
    instance._old_slug = None
    instance._old_tour_published = None
    instance._old_tour_google_drive_file_id = ''
    instance._old_tour_entry_url = None

    if instance.pk:
        try:
            old = HeritageObject.objects.only(
                'slug',
                'tourPublished',
                'tourGoogleDriveFileId',
                'tourEntryUrl',
            ).get(pk=instance.pk)
            instance._old_slug = old.slug
            instance._old_tour_published = old.tourPublished
            instance._old_tour_google_drive_file_id = old.tourGoogleDriveFileId or ''
            instance._old_tour_entry_url = old.tourEntryUrl
        except HeritageObject.DoesNotExist:
            pass

    file_id_changed = (
        (instance.tourGoogleDriveFileId or '')
        != (instance._old_tour_google_drive_file_id or '')
    )
    if file_id_changed and instance.tourGoogleDriveFileId:
        instance.tourPackUpdatedAt = timezone.now()


@receiver(post_save, sender=HeritageObject)
def heritage_object_post_save(sender, instance, **kwargs):
    cache_service.invalidate_heritage(
        slug=instance.slug,
        old_slug=getattr(instance, '_old_slug', None),
    )

    if tour_fields_changed(instance):
        if not trigger_vercel_deploy():
            instance._vercel_deploy_failed = True


@receiver(post_delete, sender=HeritageObject)
def heritage_object_post_delete(sender, instance, **kwargs):
    cache_service.invalidate_heritage(slug=instance.slug)


def _nested_post_save(sender, instance, **kwargs):
    _invalidate_by_slug(_heritage_slug_from_instance(instance))


def _nested_post_delete(sender, instance, **kwargs):
    _invalidate_by_slug(_heritage_slug_from_instance(instance))


for model in (
    ArchitectureDetail,
    BeforeAfterPair,
    HistoricalFigure,
    PhotoItem,
    AudioGuide,
    AudioGuideTrack,
    ArchitectBio,
):
    post_save.connect(_nested_post_save, sender=model)
    post_delete.connect(_nested_post_delete, sender=model)


@receiver(m2m_changed, sender=HistoricalFigure.milestones.through)
def historical_figure_milestones_changed(sender, instance, **kwargs):
    if isinstance(instance, HistoricalFigure):
        _invalidate_by_slug(_heritage_slug_from_instance(instance))


@receiver(m2m_changed, sender=ArchitectBio.milestones.through)
def architect_bio_milestones_changed(sender, instance, **kwargs):
    if isinstance(instance, ArchitectBio):
        _invalidate_by_slug(_heritage_slug_from_instance(instance))

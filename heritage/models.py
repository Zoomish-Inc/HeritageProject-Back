from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
import uuid


class HeritageObject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    name_ru = models.CharField(max_length=255, blank=True)
    name_uz = models.CharField(max_length=255, blank=True)
    formerName_ru = models.CharField(max_length=255, blank=True)
    formerName_uz = models.CharField(max_length=255, blank=True)

    currentPurpose_ru = models.CharField(max_length=255, blank=True)
    currentPurpose_uz = models.CharField(max_length=255, blank=True)
    historicalPurpose_ru = models.CharField(max_length=255, blank=True)
    historicalPurpose_uz = models.CharField(max_length=255, blank=True)

    address_ru = models.TextField(blank=True)
    address_uz = models.TextField(blank=True)

    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    mapUrl = models.URLField(blank=True)

    yearBuilt = models.IntegerField(null=True, blank=True)
    yearRange = models.CharField(max_length=50, blank=True)
    yearBuiltLabel_ru = models.CharField(max_length=255, blank=True)
    yearBuiltLabel_uz = models.CharField(max_length=255, blank=True)

    architecturalStyle_ru = models.CharField(max_length=255, blank=True)
    architecturalStyle_uz = models.CharField(max_length=255, blank=True)
    architect_ru = models.CharField(max_length=255, blank=True)
    architect_uz = models.CharField(max_length=255, blank=True)

    shortDescription_ru = models.TextField(blank=True)
    shortDescription_uz = models.TextField(blank=True)
    architecturalDescription_ru = models.TextField(blank=True)
    architecturalDescription_uz = models.TextField(blank=True)
    history_ru = models.TextField(blank=True)
    history_uz = models.TextField(blank=True)

    coverImageUrl = models.URLField(blank=True)
    visualStyleNotes_ru = models.TextField(blank=True)
    visualStyleNotes_uz = models.TextField(blank=True)

    isPublished = models.BooleanField(default=False)
    tourPublished = models.BooleanField(default=False)
    tourEntryUrl = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name_ru']

    def __str__(self):
        return self.name_ru

    def save(self, *args, **kwargs):
        if self.is_published:
            published_count = HeritageObject.objects.filter(
                is_published=True
            ).exclude(pk=self.pk).count()
            
            if published_count >= 6:
                raise ValidationError(
                    'Нельзя опубликовать больше 6 объектов. '
                    'Сначала снимите публикацию с другого объекта.'
                )

        if not self.slug:
            self.slug = slugify(self.name_ru)

class HeritageListItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    name_ru = models.CharField(max_length=255, blank=True)
    name_uz = models.CharField(max_length=255, blank=True)
    yearRange = models.CharField(max_length=50, blank=True)
    address_ru = models.CharField(max_length=255, blank=True)
    address_uz = models.CharField(max_length=255, blank=True)
    coverImageUrl = models.URLField(blank=True)
    shortDescription_ru = models.CharField(max_length=255, blank=True)
    shortDescription_uz = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    isPublished = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']


# ====================== ВЛОЖЕННЫЕ МОДЕЛИ ======================

class BiographyMilestone(models.Model):
    year = models.IntegerField()
    event_ru = models.CharField(max_length=500)
    event_uz = models.CharField(max_length=500, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['year', 'order']


class ArchitectureDetail(models.Model):

    heritage = models.ForeignKey(
        HeritageObject, 
        on_delete=models.CASCADE, 
        related_name='architectureDetails'
        )
    
    title_ru = models.CharField(max_length=255)
    title_uz = models.CharField(max_length=255, blank=True)
    description_ru = models.TextField(blank=True)
    description_uz = models.TextField(blank=True)
    imageUrl = models.URLField(blank=True)
    imageSourceUrl = models.URLField(blank=True)
    imageCredit_ru = models.CharField(max_length=255, blank=True)
    imageCredit_uz = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class BeforeAfterPair(models.Model):
    """Пара "Было / Стало" """
    
    heritage_object = models.ForeignKey(
        'HeritageObject',
        on_delete=models.CASCADE,
        related_name='beforeAfterPairs',
        verbose_name="Объект наследия"
    )
    
    label_ru = models.CharField("Название пары (RU)", max_length=255, blank=True)
    label_uz = models.CharField("Название пары (UZ)", max_length=255, blank=True)

    before = models.ForeignKey(
        'media_files.MediaFile',
        on_delete=models.CASCADE,
        related_name='before_pairs',
        verbose_name="Фото 'Было'"
    )

    after = models.ForeignKey(
        'media_files.MediaFile',
        on_delete=models.CASCADE,
        related_name='after_pairs',
        verbose_name=("Фото 'Стало'")
    )

    year_before = models.PositiveIntegerField(("Год 'Было'"), null=True, blank=True)
    year_after = models.PositiveIntegerField(("Год 'Стало'"), null=True, blank=True)

    description_ru = models.TextField(("Описание (RU)"), blank=True)
    description_uz = models.TextField(("Описание (UZ)"), blank=True)

    sort_order = models.PositiveIntegerField(("Порядок"), default=0)

    class Meta:
        ordering = ['sort_order']
        verbose_name = ("Пара Было/Стало")
        verbose_name_plural = ("Пары Было/Стало")

    def __str__(self):
        return self.title_ru or str(self.heritage_object)

    class Meta:
        ordering = ['sort_order']
        verbose_name = ("Пара Было/Стало")
        verbose_name_plural = ("Пары Было/Стало")

    def __str__(self):
        return self.title_ru or f"Пара для {self.heritage_object}"


class HistoricalFigure(models.Model):

    heritage = models.ForeignKey(
        HeritageObject, 
        on_delete=models.CASCADE, 
        related_name='historicalFigures'
        )
    
    name_ru = models.CharField(max_length=255)
    name_uz = models.CharField(max_length=255, blank=True)
    role_ru = models.CharField(max_length=255, blank=True)
    role_uz = models.CharField(max_length=255, blank=True)
    bio_ru = models.TextField(blank=True)
    bio_uz = models.TextField(blank=True)
    photoUrl = models.URLField(blank=True)
    bioSourceUrl = models.URLField(blank=True)
    bioSourceCredit_ru = models.CharField(max_length=255, blank=True)
    bioSourceCredit_uz = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    milestones = models.ManyToManyField(BiographyMilestone, blank=True)

    class Meta:
        ordering = ['order']


class PhotoItem(models.Model):

    heritage = models.ForeignKey(
        HeritageObject, 
        on_delete=models.CASCADE, 
        related_name='photos'
        )
    
    heritage_history_media = models.ForeignKey(
        HeritageObject, 
        on_delete=models.CASCADE, 
        related_name='historyMedia',
        blank=True, 
        null=True
    )
    
    url = models.URLField()
    caption_ru = models.CharField(max_length=255, blank=True)
    caption_uz = models.CharField(max_length=255, blank=True)
    isHistorical = models.BooleanField(default=False)
    year = models.IntegerField(blank=True)
    sourceUrl = models.URLField(blank=True)
    credit_ru = models.CharField(max_length=255, blank=True)
    credit_uz = models.CharField(max_length=255, blank=True)

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class AudioGuide(models.Model):
    """Аудиогид как отдельная модель (один на объект)"""

    heritage = models.OneToOneField(
        HeritageObject, 
        on_delete=models.CASCADE, 
        related_name='audioGuide'
        )
    
    narratorLabel_ru = models.CharField(max_length=255, blank=True)
    narratorLabel_uz = models.CharField(max_length=255, blank=True)
    transcript_ru = models.TextField(blank=True)
    transcript_uz = models.TextField(blank=True)
    atmosphereDescription_ru = models.TextField(blank=True)
    atmosphereDescription_uz = models.TextField(blank=True)
    musicSuggestion_ru = models.TextField(blank=True)
    musicSuggestion_uz = models.TextField(blank=True)


class AudioGuideTrack(models.Model):

    audio_guide = models.ForeignKey(
        AudioGuide, 
        on_delete=models.CASCADE, 
        related_name='track'
        )
    
    url = models.URLField()
    shortTitle_ru = models.CharField(max_length=255, blank=True)
    shortTitle_uz = models.CharField(max_length=255, blank=True)
    fullTitle_ru = models.CharField(max_length=255, blank=True)
    fullTitle_uz = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)


class ArchitectBio(models.Model):
    heritage = models.OneToOneField(
        HeritageObject, 
        on_delete=models.CASCADE, 
        related_name='architectBio'
        )
    
    name_ru = models.CharField(max_length=255)
    name_uz = models.CharField(max_length=255, blank=True)
    role_ru = models.CharField(max_length=255, blank=True)
    role_uz = models.CharField(max_length=255, blank=True)
    bio_ru = models.TextField(blank=True)
    bio_uz = models.TextField(blank=True)
    photoUrl = models.URLField(blank=True)

    milestones = models.ManyToManyField(BiographyMilestone, blank=True)
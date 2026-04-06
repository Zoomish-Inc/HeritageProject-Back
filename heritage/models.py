from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
import uuid

class HeritageObject(models.Model):
    """Основной объект культурного наследия (ОКН)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Название
    name_ru = models.CharField("Название (ru)", max_length=255)
    name_uz = models.CharField("Название (uz)", max_length=255, blank=True)
    former_name_ru = models.CharField("Прежнее название (ru)", max_length=255, blank=True)
    former_name_uz = models.CharField("Прежнее название (uz)", max_length=255, blank=True)
    
    # Назначение
    current_purpose_ru = models.CharField("Назначение сейчас (ru)", max_length=255, blank=True)
    current_purpose_uz = models.CharField("Назначение сейчас (uz)", max_length=255, blank=True)
    historical_purpose_ru = models.CharField("Назначение ранее (ru)", max_length=255, blank=True)
    historical_purpose_uz = models.CharField("Назначение ранее (uz)", max_length=255, blank=True)
    
    # Адрес
    address_ru = models.TextField("Адрес (ru)", blank=True)
    address_uz = models.TextField("Адрес (uz)", blank=True)
    
    # Год постройки
    year_built = models.IntegerField("Год постройки", null=True, blank=True)
    year_range = models.CharField("Диапазон лет (строка)", max_length=50, blank=True)
    
    # Стиль и архитектор
    architectural_style_ru = models.CharField("Стиль (ru)", max_length=255, blank=True)
    architectural_style_uz = models.CharField("Стиль (uz)", max_length=255, blank=True)
    architect_ru = models.CharField("Архитектор (ru)", max_length=255, blank=True)
    architect_uz = models.CharField("Архитектор (uz)", max_length=255, blank=True)
    
    # Описания
    architectural_description_ru = models.TextField("Архитектурное описание (ru)", blank=True)
    architectural_description_uz = models.TextField("Архитектурное описание (uz)", blank=True)
    history_ru = models.TextField("История (ru)", blank=True)
    history_uz = models.TextField("История (uz)", blank=True)
    
    # SEO и каталог
    slug = models.SlugField("Slug (URL)", max_length=255, unique=True, blank=True)
    short_description_ru = models.TextField("Краткое описание (ru)", blank=True)
    short_description_uz = models.TextField("Краткое описание (uz)", blank=True)
    order = models.PositiveIntegerField("Порядок в каталоге", default=0)
    is_published = models.BooleanField("Опубликовано", default=False)
    cover_image = models.URLField("Обложка", blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name_ru']
        verbose_name = "Объект наследия"
        verbose_name_plural = "Объекты наследия"

    def __str__(self):
        return self.name_ru

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_ru)
        super().save(*args, **kwargs)


# ==================== Связанные модели ====================

class ArchitectureDetail(models.Model):
    """7.2 Архитектура в деталях"""
    heritage = models.ForeignKey(HeritageObject, on_delete=models.CASCADE, related_name='architecture_details')
    title_ru = models.CharField(max_length=255)
    title_uz = models.CharField(max_length=255, blank=True)
    description_ru = models.TextField()
    description_uz = models.TextField(blank=True)
    image = models.ImageField(upload_to='architecture_details/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "Архитектурная деталь"
        verbose_name_plural = "Архитектурные детали"


class BeforeAfterPair(models.Model):
    """Ретроспектива (пары «до/после»)"""
    heritage = models.ForeignKey(HeritageObject, on_delete=models.CASCADE, related_name='before_after_pairs')
    title_ru = models.CharField(max_length=255, blank=True)
    title_uz = models.CharField(max_length=255, blank=True)
    before_image = models.ImageField(upload_to='before_after/')
    after_image = models.ImageField(upload_to='before_after/')
    year_before = models.IntegerField(null=True, blank=True)
    year_after = models.IntegerField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class HistoricalFigure(models.Model):
    """Личности в истории + биография архитектора"""
    heritage = models.ForeignKey(HeritageObject, on_delete=models.CASCADE, related_name='historical_figures')
    name_ru = models.CharField(max_length=255)
    name_uz = models.CharField(max_length=255, blank=True)
    role_ru = models.CharField(max_length=255, blank=True)
    role_uz = models.CharField(max_length=255, blank=True)
    bio_ru = models.TextField(blank=True)
    bio_uz = models.TextField(blank=True)
    photo = models.ImageField(upload_to='figures/', blank=True, null=True)
    is_architect_bio = models.BooleanField("Это биография архитектора", default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class AudioGuideItem(models.Model):
    """Голос наследия (аудиогид)"""
    TYPE_CHOICES = [
        ('intro', 'Краткий экскурс'),
        ('atmosphere', 'Атмосферный звук'),
        ('historian', 'Голос историка'),
    ]
    
    heritage = models.ForeignKey(HeritageObject, on_delete=models.CASCADE, related_name='audio_guides')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title_ru = models.CharField(max_length=255)
    title_uz = models.CharField(max_length=255, blank=True)
    audio_file = models.FileField(upload_to='audio/')
    transcript_ru = models.TextField("Расшифровка (ru)", blank=True)
    transcript_uz = models.TextField("Расшифровка (uz)", blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
from django.db import models
from django.utils.translation import gettext_lazy as _


class MediaFile(models.Model):
    """Централизованное хранилище медиафайлов"""

    MEDIA_TYPES = [
        ('image', _('Изображение')),
        ('video', _('Видео')),
        ('audio', _('Аудио')),
    ]

    # Названия
    title_ru = models.CharField(_("Название (RU)"), max_length=255)
    title_uz = models.CharField(_("Название (UZ)"), max_length=255, blank=True)

    # Файл
    file = models.FileField(_("Файл"), upload_to='uploads/%Y/%m/%d/')
    media_type = models.CharField(_("Тип медиа"), max_length=10, choices=MEDIA_TYPES)

    # SEO и подписи
    alt_ru = models.CharField(_("Alt (RU)"), max_length=255, blank=True)
    alt_uz = models.CharField(_("Alt (UZ)"), max_length=255, blank=True)
    caption_ru = models.TextField(_("Подпись (RU)"), blank=True)
    caption_uz = models.TextField(_("Подпись (UZ)"), blank=True)

    # Дополнительная информация
    year = models.PositiveIntegerField(_("Год"), null=True, blank=True)
    source = models.CharField(_("Источник"), max_length=500, blank=True)

    # Сортировка
    sort_order = models.PositiveIntegerField(_("Порядок сортировки"), default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'created_at']
        verbose_name = _("Медиафайл")
        verbose_name_plural = _("Медиафайлы")

    def __str__(self):
        return f"{self.title_ru} ({self.get_media_type_display()})"

    @property
    def url(self):
        """Полный URL файла (с поддержкой CDN)"""
        from django.conf import settings
        if getattr(settings, 'MEDIA_BASE_URL', None):
            base = settings.MEDIA_BASE_URL.rstrip('/')
            return f"{base}{self.file.url}"
        return self.file.url

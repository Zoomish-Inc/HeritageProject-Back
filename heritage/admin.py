from django.contrib import admin, messages
import nested_admin
from django.utils.html import format_html
from .models import (
    HeritageObject,
    ArchitectureDetail,
    BeforeAfterPair,
    HistoricalFigure,
    PhotoItem,
    AudioGuide,
    AudioGuideTrack,
    ArchitectBio,
    BiographyMilestone,
)

class ArchitectureDetailInline(nested_admin.NestedTabularInline):
    model = ArchitectureDetail
    extra = 1
    fields = ('order', 
              'title_ru', 
              'title_uz', 
              'description_ru', 
              'description_uz', 
              'imageUrl', 
              'imageSourceUrl', 
              'imageCredit_ru', 
              'imageCredit_uz',
              )


class BeforeAfterPairInline(nested_admin.NestedTabularInline):
    model = BeforeAfterPair
    extra = 1
    fields = (
        'sort_order',
        'label_ru',
        'label_uz',
        'beforeUrl',
        'afterUrl',
        'year_before',
        'year_after',
        'description_ru',
        'description_uz',
    )


class HistoricalFigureInline(nested_admin.NestedStackedInline):
    model = HistoricalFigure
    extra = 1
    fields = (
        'order',
        'name_ru',
        'name_uz',
        'role_ru',
        'role_uz',
        'bio_ru',
        'bio_uz',
        'photoUrl',
        'bioSourceUrl',
        'bioSourceCredit_ru',
        'bioSourceCredit_uz',
        'milestones',
    )


class PhotoItemInline(nested_admin.NestedTabularInline):
    model = PhotoItem
    fk_name = 'heritage'
    extra = 1
    fields = (
        'order',
        'url',
        'caption_ru',
        'caption_uz',
        'isHistorical',
        'year',
        'sourceUrl',
        'credit_ru',
        'credit_uz',
    )

class HistoryMediaInline(nested_admin.NestedTabularInline):
    model = PhotoItem
    fk_name = 'heritage_history_media'
    extra = 1
    verbose_name = "Историческое медиа"
    fields = (
        'order',
        'url',
        'caption_ru',
        'caption_uz',
        'isHistorical',
        'year',
        'sourceUrl',
        'credit_ru',
        'credit_uz',
    )


class AudioGuideTrackInline(nested_admin.NestedTabularInline):
    model = AudioGuideTrack
    extra = 1
    fields = (
        'order',
        'url',
        'shortTitle_ru',
        'shortTitle_uz',
        'fullTitle_ru',
        'fullTitle_uz',
    )


class AudioGuideInline(nested_admin.NestedStackedInline):
    model = AudioGuide
    extra = 0
    max_num = 1
    inlines = [AudioGuideTrackInline]
    fields = (
        'narratorLabel_ru',
        'narratorLabel_uz',
        'transcript_ru',
        'transcript_uz',
        'atmosphereDescription_ru',
        'atmosphereDescription_uz',
        'musicSuggestion_ru',
        'musicSuggestion_uz',
    )

class ArchitectBioInline(nested_admin.NestedStackedInline):
    model = ArchitectBio
    extra = 1
    fields = (
        'name_ru', 
        'name_uz',
        'role_ru', 
        'role_uz',
        'bio_ru', 
        'bio_uz',
        'photoUrl',
        'milestones',
    )

@admin.register(HeritageObject)
class HeritageObjectAdmin(nested_admin.NestedModelAdmin):
    list_display = ('name_ru', 'slug', 'yearBuilt', 'isPublished', 'tourPublished', 'order', 'created_at')
    list_filter = ('isPublished', 'tourPublished', 'yearBuilt')
    search_fields = ('name_ru', 'name_uz', 'slug', 'address_ru')
    ordering = ('order', 'name_ru')
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'isPublished',
                'name_ru', 'name_uz',
                'formerName_ru', 'formerName_uz',
                'slug', 'order', 'coverImageUrl'
            )
        }),
        ('Назначение и адрес', {
            'fields': (
                'currentPurpose_ru', 'currentPurpose_uz',
                'historicalPurpose_ru', 'historicalPurpose_uz',
                'address_ru', 'address_uz'
            )
        }),
        ('Год и стиль', {
            'fields': (
                'yearBuilt', 'yearRange', 'yearBuiltLabel_ru', 'yearBuiltLabel_uz',
                'architecturalStyle_ru', 'architecturalStyle_uz',
                'architect_ru', 'architect_uz'
            )
        }),
        ('Геолокация', {
            'fields': ('lat', 'lng', 'mapUrl')
        }),
        ('Описания', {
            'fields': (
                'shortDescription_ru', 'shortDescription_uz',
                'architecturalDescription_ru', 'architecturalDescription_uz',
                'history_ru', 'history_uz',
                'visualStyleNotes_ru', 'visualStyleNotes_uz'
            )
        }),
        ('3D-тур (Google Drive)', {
            'fields': (
                'tourPublished',
                'tourGoogleDriveFileId',
            )
        }),
    )
    
    inlines = [
        ArchitectureDetailInline,
        BeforeAfterPairInline,
        HistoricalFigureInline,
        PhotoItemInline,
        AudioGuideInline,
        ArchitectBioInline,
        HistoryMediaInline,
    ]
    
    # Автоматический slug
    prepopulated_fields = {'slug': ('name_ru',)}

    def save_model(self, request, obj, form, change):
        # Проверка: если пытаемся опубликовать
        if obj.isPublished:
            published_count = HeritageObject.objects.filter(isPublished=True).exclude(pk=obj.pk).count()
            if published_count >= 6:
                self.message_user(request, 
                    '❌ Нельзя опубликовать больше 6 объектов! '
                    'Сначала снимите публикацию с другого объекта.', 
                    level='error')
                return
        
        # Если проверку прошли - сохраняем
        super().save_model(request, obj, form, change)
        self.message_user(request, 'Объект сохранен', level=messages.SUCCESS)

        if getattr(obj, '_vercel_deploy_failed', False):
            self.message_user(
                request,
                'Тур сохранён, но не удалось запустить деплой фронтенда. Проверьте VERCEL_DEPLOY_HOOK_URL.',
                level=messages.WARNING,
            )





# Остальные модели используются через inlines.
# Их отдельная регистрация в admin может ломать workflow сохранения/редиректов.
# Поэтому убираем отдельные registration.


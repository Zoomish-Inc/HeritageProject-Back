from django.contrib import admin, messages
import nested_admin
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


# ====================== INLINES ======================

class ArchitectureDetailInline(nested_admin.NestedTabularInline):
    model = ArchitectureDetail
    extra = 1
    fields = ('order', 'title_ru', 'title_uz', 'description_ru', 'description_uz',
              'imageUrl', 'imageSourceUrl', 'imageCredit_ru', 'imageCredit_uz')


class BeforeAfterPairInline(nested_admin.NestedTabularInline):
    model = BeforeAfterPair
    extra = 1
    fields = ('sort_order', 'label_ru', 'label_uz', 'beforeUrl', 'afterUrl',
              'year_before', 'year_after', 'description_ru', 'description_uz')


class HistoricalFigureInline(nested_admin.NestedStackedInline):
    model = HistoricalFigure
    extra = 1
    fields = ('order', 'name_ru', 'name_uz', 'role_ru', 'role_uz',
              'bio_ru', 'bio_uz', 'photoUrl', 'bioSourceUrl',
              'bioSourceCredit_ru', 'bioSourceCredit_uz', 'milestones')


class PhotoItemInline(nested_admin.NestedTabularInline):
    model = PhotoItem
    fk_name = 'heritage'
    extra = 1
    fields = ('order', 'url', 'caption_ru', 'caption_uz', 'isHistorical',
              'year', 'sourceUrl', 'credit_ru', 'credit_uz')


class HistoryMediaInline(nested_admin.NestedTabularInline):
    model = PhotoItem
    fk_name = 'heritage_history_media'
    extra = 1
    verbose_name = "Историческое медиа"
    fields = ('order', 'url', 'caption_ru', 'caption_uz', 'isHistorical',
              'year', 'sourceUrl', 'credit_ru', 'credit_uz')


class AudioGuideTrackInline(nested_admin.NestedTabularInline):
    model = AudioGuideTrack
    extra = 1
    fields = ('order', 'url', 'shortTitle_ru', 'shortTitle_uz',
              'fullTitle_ru', 'fullTitle_uz')


class AudioGuideInline(nested_admin.NestedStackedInline):
    model = AudioGuide
    extra = 0
    max_num = 1
    inlines = [AudioGuideTrackInline]
    fields = (
        'narratorLabel_ru', 'narratorLabel_uz',
        'transcript_ru', 'transcript_uz',
        'atmosphereDescription_ru', 'atmosphereDescription_uz',
        'musicSuggestion_ru', 'musicSuggestion_uz',
    )


class ArchitectBioInline(nested_admin.NestedStackedInline):
    model = ArchitectBio
    extra = 1
    fields = (
        'name_ru', 'name_uz', 'role_ru', 'role_uz',
        'bio_ru', 'bio_uz', 'photoUrl', 'milestones'
    )


# ====================== MAIN ADMIN ======================

@admin.register(HeritageObject)
class HeritageObjectAdmin(nested_admin.NestedModelAdmin):
    list_display = ('name_ru', 'slug', 'order', 'isPublished', 'tourPublished', 
                    'yearBuilt', 'created_at')
    list_filter = ('isPublished', 'tourPublished', 'yearBuilt')
    search_fields = ('slug', 'name_ru', 'name_uz', 'address_ru')
    ordering = ('order', 'name_ru')
    
    prepopulated_fields = {'slug': ('name_ru',)}

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
                'address_ru', 'address_uz',
                'lat', 'lng', 'mapUrl'
            )
        }),
        ('Год и стиль', {
            'fields': (
                'yearBuilt', 'yearRange', 'yearBuiltLabel_ru', 'yearBuiltLabel_uz',
                'architecturalStyle_ru', 'architecturalStyle_uz',
                'architect_ru', 'architect_uz'
            )
        }),
        ('Геолокация и 3D-тур', {
            'fields': (
                'tourPublished',
                'tourGoogleDriveFileId',
                'tourEntryUrl',
            )
        }),
        ('Описания', {
            'fields': (
                'shortDescription_ru', 'shortDescription_uz',
                'architecturalDescription_ru', 'architecturalDescription_uz',
                'history_ru', 'history_uz',
                'visualStyleNotes_ru', 'visualStyleNotes_uz'
            )
        }),
    )

    inlines = [
        ArchitectureDetailInline,
        BeforeAfterPairInline,
        HistoricalFigureInline,
        PhotoItemInline,
        HistoryMediaInline,
        AudioGuideInline,
        ArchitectBioInline,
    ]

    def save_model(self, request, obj, form, change):
        if obj.isPublished:
            published_count = HeritageObject.objects.filter(
                isPublished=True
            ).exclude(pk=obj.pk).count()
            
            if published_count >= 6:
                self.message_user(request, 
                    '❌ Нельзя опубликовать больше 6 объектов! '
                    'Сначала снимите публикацию с другого объекта.', 
                    level=messages.ERROR)
                return

        super().save_model(request, obj, form, change)
        self.message_user(request, '✅ Объект успешно сохранён', level=messages.SUCCESS)


# Остальные модели регистрировать не обязательно — они доступны через inlines
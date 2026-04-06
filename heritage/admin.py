from django.contrib import admin
from django.utils.html import format_html
from .models import (
    HeritageObject,
    ArchitectureDetail,
    BeforeAfterPair,
    HistoricalFigure,
    AudioGuideItem,
)

class ArchitectureDetailInline(admin.TabularInline):
    model = ArchitectureDetail
    extra = 1
    fields = ('order', 'title_ru', 'title_uz', 'description_ru', 'image')

class BeforeAfterPairInline(admin.TabularInline):
    model = BeforeAfterPair
    extra = 1
    fields = ('order', 'title_ru', 'before_image', 'after_image', 'year_before', 'year_after')

class HistoricalFigureInline(admin.TabularInline):
    model = HistoricalFigure
    extra = 1
    fields = ('order', 'is_architect_bio', 'name_ru', 'name_uz', 'role_ru', 'photo')

class AudioGuideItemInline(admin.TabularInline):
    model = AudioGuideItem
    extra = 1
    fields = ('order', 'type', 'title_ru', 'title_uz', 'audio_file', 'transcript_ru')

@admin.register(HeritageObject)
class HeritageObjectAdmin(admin.ModelAdmin):
    list_display = ('name_ru', 'slug', 'year_built', 'is_published', 'order', 'created_at')
    list_filter = ('is_published', 'year_built')
    search_fields = ('name_ru', 'name_uz', 'slug')
    ordering = ('order', 'name_ru')
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'name_ru', 'name_uz', 'former_name_ru', 'former_name_uz',
                'slug', 'is_published', 'order', 'cover_image'
            )
        }),
        ('Назначение и адрес', {
            'fields': (
                'current_purpose_ru', 'current_purpose_uz',
                'historical_purpose_ru', 'historical_purpose_uz',
                'address_ru', 'address_uz'
            )
        }),
        ('Год и стиль', {
            'fields': (
                'year_built', 'year_range',
                'architectural_style_ru', 'architectural_style_uz',
                'architect_ru', 'architect_uz'
            )
        }),
        ('Описания', {
            'fields': (
                'architectural_description_ru', 'architectural_description_uz',
                'history_ru', 'history_uz',
                'short_description_ru', 'short_description_uz'
            )
        }),
    )
    
    inlines = [ArchitectureDetailInline, BeforeAfterPairInline, HistoricalFigureInline, AudioGuideItemInline]
    
    # Автоматический slug
    prepopulated_fields = {'slug': ('name_ru',)}

# Регистрируем остальные модели (для прямого редактирования)
admin.site.register(ArchitectureDetail)
admin.site.register(BeforeAfterPair)
admin.site.register(HistoricalFigure)
admin.site.register(AudioGuideItem)
from django.contrib import admin

from .models import MediaFile


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('title_ru', 'media_type', 'source_preview', 'sort_order', 'created_at')
    list_filter = ('media_type',)
    search_fields = ('title_ru', 'title_uz', 'source', 'caption_ru')
    ordering = ('sort_order', 'title_ru')
    fieldsets = (
        (None, {
            'fields': (
                'title_ru',
                'title_uz',
                'media_type',
                'source',
                'file',
            ),
        }),
        ('Подписи', {
            'fields': ('alt_ru', 'alt_uz', 'caption_ru', 'caption_uz', 'year', 'sort_order'),
        }),
    )

    @admin.display(description='URL')
    def source_preview(self, obj):
        if obj.source:
            return obj.source[:80] + ('…' if len(obj.source) > 80 else '')
        if obj.file:
            return obj.file.name
        return '—'

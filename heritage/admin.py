import logging

from django.contrib import admin, messages
from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.contenttypes.models import ContentType
import nested_admin

from accounts.roles import (
    can_add_heritage_object,
    can_delete_heritage_object,
    can_edit_content,
    can_edit_publish,
    can_edit_tour,
    can_mutate_inlines,
    is_tour_only,
)
from .models import (
    HeritageObject,
    ArchitectureDetail,
    BeforeAfterPair,
    HistoricalFigure,
    PhotoItem,
    AudioGuide,
    AudioGuideTrack,
    ArchitectBio,
)

logger = logging.getLogger(__name__)

PUBLISH_FIELDS = ('isPublished',)
TOUR_FIELDS = ('tourPublished', 'tourGoogleDriveFileId')
CONTENT_FIELDS = (
    'name_ru', 'name_uz',
    'formerName_ru', 'formerName_uz',
    'slug', 'order', 'coverImageUrl',
    'currentPurpose_ru', 'currentPurpose_uz',
    'historicalPurpose_ru', 'historicalPurpose_uz',
    'address_ru', 'address_uz',
    'yearBuilt', 'yearRange', 'yearBuiltLabel_ru', 'yearBuiltLabel_uz',
    'architecturalStyle_ru', 'architecturalStyle_uz',
    'architect_ru', 'architect_uz',
    'lat', 'lng', 'mapUrl',
    'shortDescription_ru', 'shortDescription_uz',
    'architecturalDescription_ru', 'architecturalDescription_uz',
    'history_ru', 'history_uz',
    'visualStyleNotes_ru', 'visualStyleNotes_uz',
)


class RoleAwareInlineMixin:
    def has_add_permission(self, request, obj=None):
        return can_mutate_inlines(request.user)

    def has_change_permission(self, request, obj=None):
        return can_mutate_inlines(request.user)

    def has_delete_permission(self, request, obj=None):
        return can_mutate_inlines(request.user)

    def has_view_permission(self, request, obj=None):
        if can_mutate_inlines(request.user) or can_edit_tour(request.user):
            return True
        return request.user.has_perm(f'heritage.view_{self.model._meta.model_name}')

    def get_readonly_fields(self, request, obj=None):
        if can_mutate_inlines(request.user):
            return self.readonly_fields
        return tuple(self.fields) if self.fields else self.readonly_fields


class ArchitectureDetailInline(RoleAwareInlineMixin, nested_admin.NestedTabularInline):
    model = ArchitectureDetail
    extra = 1
    fields = (
        'order',
        'title_ru',
        'title_uz',
        'description_ru',
        'description_uz',
        'imageUrl',
        'imageSourceUrl',
        'imageCredit_ru',
        'imageCredit_uz',
    )


class BeforeAfterPairInline(RoleAwareInlineMixin, nested_admin.NestedTabularInline):
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


class HistoricalFigureInline(RoleAwareInlineMixin, nested_admin.NestedStackedInline):
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


class PhotoItemInline(RoleAwareInlineMixin, nested_admin.NestedTabularInline):
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


class HistoryMediaInline(RoleAwareInlineMixin, nested_admin.NestedTabularInline):
    model = PhotoItem
    fk_name = 'heritage_history_media'
    extra = 1
    verbose_name = 'Историческое медиа'
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


class AudioGuideTrackInline(RoleAwareInlineMixin, nested_admin.NestedTabularInline):
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


class AudioGuideInline(RoleAwareInlineMixin, nested_admin.NestedStackedInline):
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


class ArchitectBioInline(RoleAwareInlineMixin, nested_admin.NestedStackedInline):
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
    list_display = (
        'name_ru', 'slug', 'yearBuilt', 'isPublished', 'tourPublished', 'order', 'created_at',
    )
    list_filter = ('isPublished', 'tourPublished', 'yearBuilt')
    search_fields = ('name_ru', 'name_uz', 'slug', 'address_ru')
    ordering = ('order', 'name_ru')
    prepopulated_fields = {'slug': ('name_ru',)}

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'isPublished',
                'name_ru', 'name_uz',
                'formerName_ru', 'formerName_uz',
                'slug', 'order', 'coverImageUrl',
            ),
        }),
        ('Назначение и адрес', {
            'fields': (
                'currentPurpose_ru', 'currentPurpose_uz',
                'historicalPurpose_ru', 'historicalPurpose_uz',
                'address_ru', 'address_uz',
            ),
        }),
        ('Год и стиль', {
            'fields': (
                'yearBuilt', 'yearRange', 'yearBuiltLabel_ru', 'yearBuiltLabel_uz',
                'architecturalStyle_ru', 'architecturalStyle_uz',
                'architect_ru', 'architect_uz',
            ),
        }),
        ('Геолокация', {
            'fields': ('lat', 'lng', 'mapUrl'),
        }),
        ('Описания', {
            'fields': (
                'shortDescription_ru', 'shortDescription_uz',
                'architecturalDescription_ru', 'architecturalDescription_uz',
                'history_ru', 'history_uz',
                'visualStyleNotes_ru', 'visualStyleNotes_uz',
            ),
        }),
        ('3D-тур (Google Drive)', {
            'fields': (
                'tourPublished',
                'tourGoogleDriveFileId',
            ),
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

    def get_prepopulated_fields(self, request, obj=None):
        if can_edit_content(request.user):
            return self.prepopulated_fields
        return {}

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        user = request.user

        if user.is_superuser:
            return readonly

        if not can_edit_content(user):
            readonly.extend(CONTENT_FIELDS)

        if not can_edit_publish(user):
            readonly.extend(PUBLISH_FIELDS)

        if not can_edit_tour(user):
            readonly.extend(TOUR_FIELDS)

        return tuple(dict.fromkeys(readonly))

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if is_tour_only(request.user) and not can_edit_content(request.user):
            return (
                ('Основная информация', {
                    'fields': ('slug', 'name_ru', 'name_uz', 'isPublished', 'order'),
                    'description': 'Только просмотр. Редактируйте блок 3D-тура ниже.',
                }),
                ('3D-тур (Google Drive)', {
                    'fields': ('tourPublished', 'tourGoogleDriveFileId'),
                }),
            )
        return fieldsets

    def has_add_permission(self, request):
        return can_add_heritage_object(request.user)

    def has_delete_permission(self, request, obj=None):
        return can_delete_heritage_object(request.user)

    def has_view_permission(self, request, obj=None):
        user = request.user
        if user.is_superuser:
            return True
        if can_edit_content(user) or can_edit_tour(user):
            return True
        return user.has_perm('heritage.view_heritageobject')

    def has_change_permission(self, request, obj=None):
        user = request.user
        if user.is_superuser:
            return True
        return can_edit_content(user) or can_edit_tour(user)

    def save_model(self, request, obj, form, change):
        if obj.isPublished:
            published_count = HeritageObject.objects.filter(
                isPublished=True,
            ).exclude(pk=obj.pk).count()
            if published_count >= 6:
                self.message_user(
                    request,
                    'Нельзя опубликовать больше 6 объектов! '
                    'Сначала снимите публикацию с другого объекта.',
                    level=messages.ERROR,
                )
                return

        old = None
        if change and obj.pk:
            old = HeritageObject.objects.filter(pk=obj.pk).only(
                'isPublished',
                'tourPublished',
                'tourGoogleDriveFileId',
                'slug',
            ).first()

        super().save_model(request, obj, form, change)
        self.message_user(request, 'Объект сохранен', level=messages.SUCCESS)

        self._log_critical_changes(request, obj, old)

        if getattr(obj, '_vercel_deploy_failed', False):
            self.message_user(
                request,
                'Тур сохранён, но не удалось запустить деплой фронтенда. '
                'Проверьте VERCEL_DEPLOY_HOOK_URL.',
                level=messages.WARNING,
            )

    def _log_critical_changes(self, request, obj, old):
        if old is None:
            logger.info(
                'heritage_admin_create user=%s groups=%s slug=%s '
                'isPublished=%s tourPublished=%s',
                request.user.username,
                list(request.user.groups.values_list('name', flat=True)),
                obj.slug,
                obj.isPublished,
                obj.tourPublished,
            )
            return

        changes = []
        for field in ('isPublished', 'tourPublished', 'tourGoogleDriveFileId'):
            before = getattr(old, field)
            after = getattr(obj, field)
            if before != after:
                changes.append(f'{field}:{before!r}->{after!r}')

        if changes:
            logger.info(
                'heritage_admin_critical_change user=%s groups=%s slug=%s %s',
                request.user.username,
                list(request.user.groups.values_list('name', flat=True)),
                obj.slug,
                ' '.join(changes),
            )


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'action_time'
    list_display = (
        'action_time', 'user', 'content_type', 'object_repr', 'action_flag', 'change_message',
    )
    list_filter = ('action_flag', 'content_type')
    search_fields = ('object_repr', 'change_message', 'user__username')
    readonly_fields = (
        'action_time', 'user', 'content_type', 'object_id', 'object_repr',
        'action_flag', 'change_message',
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or can_edit_publish(request.user)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or can_edit_publish(request.user)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        ct = ContentType.objects.get_for_model(HeritageObject)
        return qs.filter(content_type=ct).exclude(action_flag=DELETION)

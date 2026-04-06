from rest_framework import serializers
from django.conf import settings
from .models import (
    HeritageObject,
    ArchitectureDetail,
    BeforeAfterPair,
    HistoricalFigure,
    AudioGuideItem,
)


class LocalizedStringField(serializers.SerializerMethodField):
    """Превращает name_ru / name_uz в {"ru": "...", "uz": "..."}"""
    def __init__(self, ru_field: str, uz_field: str, **kwargs):
        self.ru_field = ru_field
        self.uz_field = uz_field
        super().__init__(**kwargs)

    def to_representation(self, obj):
        return {
            'ru': getattr(obj, self.ru_field, ''),
            'uz': getattr(obj, self.uz_field, ''),
        }


# ====================== Вложенные сериализаторы ======================

class ArchitectureDetailSerializer(serializers.ModelSerializer):
    title = LocalizedStringField(ru_field='title_ru', uz_field='title_uz')
    description = LocalizedStringField(ru_field='description_ru', uz_field='description_uz')

    image = serializers.SerializerMethodField()

    class Meta:
        model = ArchitectureDetail
        fields = ['title', 'description', 'image', 'order']

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class BeforeAfterPairSerializer(serializers.ModelSerializer):
    title = LocalizedStringField(ru_field='title_ru', uz_field='title_uz')
    before_image = serializers.SerializerMethodField()
    after_image = serializers.SerializerMethodField()

    class Meta:
        model = BeforeAfterPair
        fields = ['title', 'before_image', 'after_image', 'year_before', 'year_after', 'order']

    def get_before_image(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.before_image.url) if obj.before_image and request else None

    def get_after_image(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.after_image.url) if obj.after_image and request else None


class HistoricalFigureSerializer(serializers.ModelSerializer):
    name = LocalizedStringField(ru_field='name_ru', uz_field='name_uz')
    role = LocalizedStringField(ru_field='role_ru', uz_field='role_uz')
    bio = LocalizedStringField(ru_field='bio_ru', uz_field='bio_uz')
    photo = serializers.SerializerMethodField()

    class Meta:
        model = HistoricalFigure
        fields = ['name', 'role', 'bio', 'photo', 'is_architect_bio', 'order']

    def get_photo(self, obj):
        if obj.photo:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.photo.url) if request else obj.photo.url
        return None


class AudioGuideItemSerializer(serializers.ModelSerializer):
    title = LocalizedStringField(ru_field='title_ru', uz_field='title_uz')
    transcript = LocalizedStringField(ru_field='transcript_ru', uz_field='transcript_uz')
    audio_file = serializers.SerializerMethodField()

    class Meta:
        model = AudioGuideItem
        fields = ['type', 'title', 'audio_file', 'transcript', 'order']

    def get_audio_file(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.audio_file.url) if obj.audio_file and request else None


# ====================== Основные сериализаторы ======================

class HeritageListItemSerializer(serializers.ModelSerializer):
    name = LocalizedStringField(ru_field='name_ru', uz_field='name_uz')
    address = LocalizedStringField(ru_field='address_ru', uz_field='address_uz')
    short_description = LocalizedStringField(ru_field='short_description_ru', uz_field='short_description_uz')

    cover = serializers.SerializerMethodField()

    class Meta:
        model = HeritageObject
        fields = [
            'id', 'slug', 'name', 'year_built', 'year_range',
            'address', 'short_description', 'cover', 'order'
        ]

    def get_cover(self, obj):
        value = obj.cover_image
        if not value:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(value) if request else value


class HeritageObjectSerializer(serializers.ModelSerializer):
    name = LocalizedStringField(ru_field='name_ru', uz_field='name_uz')
    former_name = LocalizedStringField(ru_field='former_name_ru', uz_field='former_name_uz')
    current_purpose = LocalizedStringField(ru_field='current_purpose_ru', uz_field='current_purpose_uz')
    historical_purpose = LocalizedStringField(ru_field='historical_purpose_ru', uz_field='historical_purpose_uz')
    address = LocalizedStringField(ru_field='address_ru', uz_field='address_uz')
    architectural_style = LocalizedStringField(ru_field='architectural_style_ru', uz_field='architectural_style_uz')
    architect = LocalizedStringField(ru_field='architect_ru', uz_field='architect_uz')
    architectural_description = LocalizedStringField(ru_field='architectural_description_ru', uz_field='architectural_description_uz')
    history = LocalizedStringField(ru_field='history_ru', uz_field='history_uz')
    short_description = LocalizedStringField(ru_field='short_description_ru', uz_field='short_description_uz')
    cover = serializers.SerializerMethodField()

    # Вложенные блоки
    architecture_details = ArchitectureDetailSerializer(many=True, read_only=True)
    before_after_pairs = BeforeAfterPairSerializer(many=True, read_only=True)
    historical_figures = HistoricalFigureSerializer(many=True, read_only=True)
    audio_guides = AudioGuideItemSerializer(many=True, read_only=True)

    class Meta:
        model = HeritageObject
        fields = [
            'id', 'slug', 'name', 'former_name',
            'current_purpose', 'historical_purpose',
            'address', 'year_built', 'year_range',
            'architectural_style', 'architect',
            'architectural_description', 'history',
            'short_description',          # ← теперь правильно
            'order', 'is_published',
            'cover',
            'architecture_details',
            'before_after_pairs',
            'historical_figures',
            'audio_guides',
            'created_at', 'updated_at',
        ]

    def get_cover(self, obj):
        value = obj.cover_image
        if not value:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(value) if request else value
from rest_framework import serializers
from .models import (
    HeritageObject,
    HeritageListItem,
    BiographyMilestone,
    ArchitectureDetail,
    BeforeAfterPair,
    HistoricalFigure,
    PhotoItem,
    AudioGuide,
    AudioGuideTrack,
    ArchitectBio,
)


class LocalizedStringField(serializers.SerializerMethodField):
    """Превращает *_ru / *_uz поля в {"ru": "...", "uz": "..."}"""
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

class BiographyMilestoneSerializer(serializers.ModelSerializer):
    event = LocalizedStringField(ru_field='event_ru', uz_field='event_uz')

    class Meta:
        model = BiographyMilestone
        fields = ['year', 'event', 'order']


class ArchitectureDetailSerializer(serializers.ModelSerializer):
    title = LocalizedStringField(ru_field='title_ru', uz_field='title_uz')
    description = LocalizedStringField(ru_field='description_ru', uz_field='description_uz')
    image_credit = LocalizedStringField(ru_field='imageCredit_ru', uz_field='imageCredit_uz')

    image = serializers.SerializerMethodField()

    class Meta:
        model = ArchitectureDetail
        fields = ['title', 'description', 'image', 'image_credit', 'order']

    def get_image(self, obj):
        if obj.imageUrl:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.imageUrl) if request else obj.imageUrl
        return None


class BeforeAfterPairSerializer(serializers.ModelSerializer):
    title = LocalizedStringField(ru_field='label_ru', uz_field='label_uz')
    description = LocalizedStringField(ru_field='description_ru', uz_field='description_uz')

    before_image = serializers.SerializerMethodField()
    after_image = serializers.SerializerMethodField()

    class Meta:
        model = BeforeAfterPair
        fields = ['title', 'before_image', 'after_image', 
                  'year_before', 'year_after', 'description', 'sort_order']

    def get_before_image(self, obj):
        if getattr(obj.before, 'file', None):
            request = self.context.get('request')
            url = obj.before.file.url
            return request.build_absolute_uri(url) if request else url
        return None

    def get_after_image(self, obj):
        if getattr(obj.after, 'file', None):
            request = self.context.get('request')
            url = obj.after.file.url
            return request.build_absolute_uri(url) if request else url
        return None


class HistoricalFigureSerializer(serializers.ModelSerializer):
    name = LocalizedStringField(ru_field='name_ru', uz_field='name_uz')
    role = LocalizedStringField(ru_field='role_ru', uz_field='role_uz')
    bio = LocalizedStringField(ru_field='bio_ru', uz_field='bio_uz')
    photo = serializers.SerializerMethodField()

    milestones = BiographyMilestoneSerializer(many=True, read_only=True)

    class Meta:
        model = HistoricalFigure
        fields = ['name', 'role', 'bio', 'photo', 'order', 'milestones']

    def get_photo(self, obj):
        if obj.photoUrl:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.photoUrl) if request else obj.photoUrl
        return None


class PhotoItemSerializer(serializers.ModelSerializer):
    caption = LocalizedStringField(ru_field='caption_ru', uz_field='caption_uz')
    credit = LocalizedStringField(ru_field='credit_ru', uz_field='credit_uz')

    class Meta:
        model = PhotoItem
        fields = ['url', 'caption', 'credit', 'isHistorical', 'year', 'order']


class AudioGuideTrackSerializer(serializers.ModelSerializer):
    short_title = LocalizedStringField(ru_field='shortTitle_ru', uz_field='shortTitle_uz')
    full_title = LocalizedStringField(ru_field='fullTitle_ru', uz_field='fullTitle_uz')

    class Meta:
        model = AudioGuideTrack
        fields = ['url', 'short_title', 'full_title', 'order']


class AudioGuideSerializer(serializers.ModelSerializer):
    narrator_label = LocalizedStringField(ru_field='narratorLabel_ru', uz_field='narratorLabel_uz')
    transcript = LocalizedStringField(ru_field='transcript_ru', uz_field='transcript_uz')
    atmosphere_description = LocalizedStringField(ru_field='atmosphereDescription_ru', uz_field='atmosphereDescription_uz')
    music_suggestion = LocalizedStringField(ru_field='musicSuggestion_ru', uz_field='musicSuggestion_uz')

    tracks = AudioGuideTrackSerializer(many=True, read_only=True, source='track')

    class Meta:
        model = AudioGuide
        fields = [
            'narrator_label', 'transcript', 'atmosphere_description',
            'music_suggestion', 'tracks'
        ]


class ArchitectBioSerializer(serializers.ModelSerializer):
    name = LocalizedStringField(ru_field='name_ru', uz_field='name_uz')
    role = LocalizedStringField(ru_field='role_ru', uz_field='role_uz')
    bio = LocalizedStringField(ru_field='bio_ru', uz_field='bio_uz')

    milestones = BiographyMilestoneSerializer(many=True, read_only=True)

    class Meta:
        model = ArchitectBio
        fields = ['name', 'role', 'bio', 'photoUrl', 'milestones']


# ====================== Основные сериализаторы ======================

class HeritageListItemSerializer(serializers.ModelSerializer):
    name = LocalizedStringField(ru_field='name_ru', uz_field='name_uz')
    address = LocalizedStringField(ru_field='address_ru', uz_field='address_uz')
    short_description = LocalizedStringField(ru_field='shortDescription_ru', uz_field='shortDescription_uz')

    cover = serializers.SerializerMethodField()

    class Meta:
        model = HeritageListItem
        fields = [
            'id', 'slug', 'name', 'yearRange', 'address',
            'short_description', 'cover', 'order', 'isPublished'
        ]

    def get_cover(self, obj):
        if obj.coverImageUrl:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.coverImageUrl) if request else obj.coverImageUrl
        return None


class HeritageObjectSerializer(serializers.ModelSerializer):
    name = LocalizedStringField(ru_field='name_ru', uz_field='name_uz')
    former_name = LocalizedStringField(ru_field='formerName_ru', uz_field='formerName_uz')
    current_purpose = LocalizedStringField(ru_field='currentPurpose_ru', uz_field='currentPurpose_uz')
    historical_purpose = LocalizedStringField(ru_field='historicalPurpose_ru', uz_field='historicalPurpose_uz')
    address = LocalizedStringField(ru_field='address_ru', uz_field='address_uz')
    architectural_style = LocalizedStringField(ru_field='architecturalStyle_ru', uz_field='architecturalStyle_uz')
    architect = LocalizedStringField(ru_field='architect_ru', uz_field='architect_uz')
    architectural_description = LocalizedStringField(ru_field='architecturalDescription_ru', uz_field='architecturalDescription_uz')
    history = LocalizedStringField(ru_field='history_ru', uz_field='history_uz')
    short_description = LocalizedStringField(ru_field='shortDescription_ru', uz_field='shortDescription_uz')
    year_built_label = LocalizedStringField(ru_field='yearBuiltLabel_ru', uz_field='yearBuiltLabel_uz')
    visual_style_notes = LocalizedStringField(ru_field='visualStyleNotes_ru', uz_field='visualStyleNotes_uz')

    cover = serializers.SerializerMethodField()

    # Вложенные
    architecture_details = ArchitectureDetailSerializer(many=True, read_only=True, source='architectureDetails')
    before_after_pairs = BeforeAfterPairSerializer(many=True, read_only=True, source='beforeAfterPairs')
    historical_figures = HistoricalFigureSerializer(many=True, read_only=True, source='historicalFigures')
    photos = PhotoItemSerializer(many=True, read_only=True, source='photos')
    audio_guide = AudioGuideSerializer(read_only=True, source='audioGuide')
    architect_bio = ArchitectBioSerializer(read_only=True, source='architectBio')

    class Meta:
        model = HeritageObject
        fields = [
            'id', 'slug', 'name', 'former_name',
            'current_purpose', 'historical_purpose',
            'address', 'lat', 'lng', 'mapUrl',
            'yearBuilt', 'yearRange', 'year_built_label',
            'architectural_style', 'architect',
            'architectural_description', 'history',
            'short_description', 'visual_style_notes',
            'order', 'isPublished', 'tourPublished', 'tourEntryUrl',
            'cover',
            'architecture_details',
            'before_after_pairs',
            'historical_figures',
            'photos',
            'audio_guide',
            'architect_bio',
            'created_at', 'updated_at',
        ]

    def get_cover(self, obj):
        if obj.coverImageUrl:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.coverImageUrl) if request else obj.coverImageUrl
        return None
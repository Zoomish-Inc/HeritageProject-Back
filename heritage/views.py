from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from uuid import UUID

from .models import HeritageObject
from .serializers import HeritageListItemSerializer, HeritageObjectSerializer


class ApiResponseMixin:
    def get_response(self, data=None, success=True, message=None, status_code=200):
        return Response({
            'success': success,
            'data': data,
            'message': message,
        }, status=status_code)


class HeritageListView(APIView, ApiResponseMixin):
    def get(self, request):
        queryset = HeritageObject.objects.filter(is_published=True).order_by('order')
        serializer = HeritageListItemSerializer(queryset, many=True, context={'request': request})
        return self.get_response(data=serializer.data)


class HeritageDetailView(APIView, ApiResponseMixin):
    def get(self, request, identifier):
        try:
            # Пытаемся определить, является ли identifier UUID
            uuid_obj = UUID(str(identifier))          # str() на случай, если передан UUID объект
            obj = get_object_or_404(HeritageObject, pk=uuid_obj, is_published=True)
        except (ValueError, TypeError):
            # Если не UUID — ищем по slug
            obj = get_object_or_404(HeritageObject, slug=identifier, is_published=True)

        serializer = HeritageObjectSerializer(obj, context={'request': request})
        return self.get_response(data=serializer.data)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connections
from django.db.utils import OperationalError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from .models import HeritageObject
from .serializers import HeritageObjectSerializer, HeritageObjectListSerializer
from . import cache_service
from .db_keepalive import ping_database


class ApiResponseMixin:
    def get_response(self, data=None, success=True, message=None, status_code=200, cache_status=None):
        response = Response(
            {
                'success': success,
                'data': data,
                'message': message,
            },
            status=status_code,
        )
        if cache_status:
            response['X-Cache'] = cache_status
        return response


class HeritageListView(APIView, ApiResponseMixin):
    serializer_class = HeritageObjectListSerializer

    def get(self, request):
        def load():
            queryset = HeritageObject.objects.filter(isPublished=True).order_by('order')[:6]
            serializer = self.serializer_class(queryset, many=True, context={'request': request})
            return serializer.data

        data, cache_status = cache_service.get_or_compute(cache_service.LIST_KEY, load)
        return self.get_response(data=data, cache_status=cache_status)


class HeritageDetailView(APIView, ApiResponseMixin):
    serializer_class = HeritageObjectSerializer

    def get(self, request, slug):
        obj = HeritageObject.objects.filter(slug=slug, isPublished=True).first()
        if obj is None:
            return self.get_response(
                data=None,
                success=False,
                message='not_found',
                status_code=status.HTTP_404_NOT_FOUND,
            )

        def load():
            serializer = self.serializer_class(obj, context={'request': request})
            return serializer.data

        data, cache_status = cache_service.get_or_compute(cache_service.detail_key(slug), load)
        return self.get_response(data=data, cache_status=cache_status)


@method_decorator(never_cache, name='dispatch')
class AppView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            ping_database()
        except Exception:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==============================================
# HEALTH CHECK ENDPOINT FOR MONITORING
# ==============================================

@api_view(['GET'])
@permission_classes([AllowAny])
@never_cache
def health_check(request):
    """
    Health check endpoint for monitoring and Render.com
    Checks database connectivity with SELECT 1.
    Returns 200 OK if healthy, 503 if database is down.
    No caching - response is never cached.
    """
    # Проверка подключения к базе данных
    try:
        with connections['default'].cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "connected"
        http_status = status.HTTP_200_OK
        response_status = "ok"
    except OperationalError:
        db_status = "disconnected"
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE
        response_status = "degraded"
    
    # Опциональная проверка Redis (не влияет на статус)
    redis_status = "not_configured"
    try:
        from django.core.cache import cache
        # Тестируем Redis без сохранения в кэше
        cache.set('health_check_ping', 'pong', timeout=1)
        if cache.get('health_check_ping') == 'pong':
            redis_status = "connected"
    except ImportError:
        redis_status = "not_installed"
    except Exception:
        redis_status = "disconnected"
    
    return Response(
        {
            "status": response_status,
            "database": db_status,
            "redis": redis_status,
        },
        status=http_status,
    )
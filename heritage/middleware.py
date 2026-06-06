import logging
import time

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

logger = logging.getLogger(__name__)

PUBLIC_GET_PREFIXES = (
    '/api/v1/heritage/',
    '/api/v1/tour-packs/',
)


def get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


class PublicApiRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._should_rate_limit(request) and self._is_rate_limited(request):
            return JsonResponse(
                {
                    'success': False,
                    'data': None,
                    'message': 'rate_limit_exceeded',
                },
                status=429,
            )
        return self.get_response(request)

    def _should_rate_limit(self, request):
        if request.method != 'GET':
            return False
        if not getattr(settings, 'API_RATE_LIMIT_ENABLED', True):
            return False
        path = request.path
        return any(
            path == prefix.rstrip('/') or path.startswith(prefix)
            for prefix in PUBLIC_GET_PREFIXES
        )

    def _is_rate_limited(self, request):
        limit = getattr(settings, 'API_RATE_LIMIT_PER_MINUTE', 120)
        if limit <= 0:
            return False

        ip = get_client_ip(request)
        window = int(time.time()) // 60
        key = f'ratelimit:public-api:{ip}:{window}'

        try:
            if cache.add(key, 1, timeout=60):
                return False
            count = cache.incr(key)
            return count > limit
        except Exception:
            logger.exception('rate limit check failed for %s', key)
            return False

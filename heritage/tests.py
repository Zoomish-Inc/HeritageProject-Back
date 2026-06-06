import json

from django.test import RequestFactory, SimpleTestCase, override_settings

from heritage.http_cache import apply_public_cache_headers, compute_etag, not_modified_if_etag_matches
from heritage.middleware import PublicApiRateLimitMiddleware
from rest_framework.response import Response


class HttpCacheTests(SimpleTestCase):
    def test_compute_etag_is_stable(self):
        data = [{'slug': 'a', 'order': 1}]
        self.assertEqual(compute_etag(data), compute_etag(data))

    def test_not_modified_returns_304(self):
        data = [{'slug': 'a'}]
        request = RequestFactory().get(
            '/api/v1/heritage/',
            HTTP_IF_NONE_MATCH=compute_etag(data),
        )
        response = not_modified_if_etag_matches(request, data)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 304)
        self.assertIn('Cache-Control', response)

    def test_apply_public_cache_headers(self):
        response = Response({'success': True, 'data': []})
        apply_public_cache_headers(response, [])
        self.assertIn('max-age=3600', response['Cache-Control'])
        self.assertTrue(response['ETag'].startswith('"'))


@override_settings(
    API_RATE_LIMIT_ENABLED=True,
    API_RATE_LIMIT_PER_MINUTE=2,
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
)
class PublicApiRateLimitMiddlewareTests(SimpleTestCase):
    def test_blocks_after_limit(self):
        middleware = PublicApiRateLimitMiddleware(lambda request: Response({'ok': True}))
        request = RequestFactory().get('/api/v1/heritage/')

        self.assertEqual(middleware(request).status_code, 200)
        self.assertEqual(middleware(request).status_code, 200)
        blocked = middleware(request)
        self.assertEqual(blocked.status_code, 429)
        payload = json.loads(blocked.content)
        self.assertFalse(payload['success'])
        self.assertEqual(payload['message'], 'rate_limit_exceeded')

    def test_skips_health_endpoint(self):
        middleware = PublicApiRateLimitMiddleware(lambda request: Response({'ok': True}))
        request = RequestFactory().get('/api/v1/health/')
        for _ in range(5):
            self.assertEqual(middleware(request).status_code, 200)

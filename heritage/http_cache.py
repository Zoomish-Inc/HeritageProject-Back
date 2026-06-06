import hashlib
import json

from django.conf import settings
from django.http import HttpResponse
from rest_framework.response import Response


def compute_etag(data):
    payload = json.dumps(data, sort_keys=True, default=str, ensure_ascii=False)
    digest = hashlib.md5(payload.encode('utf-8')).hexdigest()
    return f'"{digest}"'


def get_cache_max_age():
    return getattr(settings, 'HERITAGE_HTTP_CACHE_MAX_AGE', 3600)


def apply_public_cache_headers(response, data):
    if not isinstance(response, Response):
        return response

    max_age = get_cache_max_age()
    etag = compute_etag(data)
    response['Cache-Control'] = f'public, max-age={max_age}, must-revalidate'
    response['ETag'] = etag
    return response


def not_modified_if_etag_matches(request, data):
    etag = compute_etag(data)
    if request.META.get('HTTP_IF_NONE_MATCH') == etag:
        response = HttpResponse(status=304)
        response['Cache-Control'] = f'public, max-age={get_cache_max_age()}, must-revalidate'
        response['ETag'] = etag
        return response
    return None

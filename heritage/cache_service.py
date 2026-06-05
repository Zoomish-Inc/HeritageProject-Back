import logging
import time
from typing import Any, Callable, Optional, Tuple

from django.core.cache import cache

logger = logging.getLogger(__name__)

CACHE_TTL = 3600
LIST_KEY = 'list:v1'
LOCK_TIMEOUT = 30
LOCK_WAIT_RETRIES = 5
LOCK_WAIT_SECONDS = 0.1


def detail_key(slug: str) -> str:
    return f'detail:{slug}:v1'


def _lock_key(key: str) -> str:
    return f'{key}:lock'


def get_list() -> Optional[Any]:
    try:
        return cache.get(LIST_KEY)
    except Exception:
        logger.exception('cache get failed for %s', LIST_KEY)
        return None


def set_list(data: Any) -> None:
    try:
        cache.set(LIST_KEY, data, timeout=CACHE_TTL)
    except Exception:
        logger.exception('cache set failed for %s', LIST_KEY)


def get_detail(slug: str) -> Optional[Any]:
    key = detail_key(slug)
    try:
        return cache.get(key)
    except Exception:
        logger.exception('cache get failed for %s', key)
        return None


def set_detail(slug: str, data: Any) -> None:
    key = detail_key(slug)
    try:
        cache.set(key, data, timeout=CACHE_TTL)
    except Exception:
        logger.exception('cache set failed for %s', key)


def invalidate_heritage(slug: Optional[str] = None, old_slug: Optional[str] = None) -> None:
    try:
        cache.delete(LIST_KEY)
        if slug:
            cache.delete(detail_key(slug))
        if old_slug and old_slug != slug:
            cache.delete(detail_key(old_slug))
    except Exception:
        logger.exception('cache invalidation failed')


def get_or_compute(key: str, compute_fn: Callable[[], Any]) -> Tuple[Any, str]:
    try:
        cached = cache.get(key)
        if cached is not None:
            return cached, 'HIT'
    except Exception:
        logger.exception('cache get failed for %s', key)

    lock_key = _lock_key(key)
    acquired = False
    try:
        acquired = cache.add(lock_key, '1', timeout=LOCK_TIMEOUT)
    except Exception:
        logger.exception('cache lock failed for %s', key)

    if acquired:
        try:
            try:
                cached = cache.get(key)
                if cached is not None:
                    return cached, 'HIT'
            except Exception:
                logger.exception('cache get failed for %s', key)

            data = compute_fn()
            try:
                cache.set(key, data, timeout=CACHE_TTL)
            except Exception:
                logger.exception('cache set failed for %s', key)
            return data, 'MISS'
        finally:
            try:
                cache.delete(lock_key)
            except Exception:
                pass

    for _ in range(LOCK_WAIT_RETRIES):
        time.sleep(LOCK_WAIT_SECONDS)
        try:
            cached = cache.get(key)
            if cached is not None:
                return cached, 'HIT'
        except Exception:
            logger.exception('cache get failed for %s', key)

    return compute_fn(), 'MISS'

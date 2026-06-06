import logging
import re
from urllib.parse import parse_qs, urlparse

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

_DRIVE_FILE_PATH_RE = re.compile(r'/file/d/([a-zA-Z0-9_-]+)')
_DRIVE_OPEN_ID_RE = re.compile(r'[?&]id=([a-zA-Z0-9_-]+)')
_DRIVE_ID_RE = re.compile(r'^[a-zA-Z0-9_-]{10,128}$')


def normalize_google_drive_file_id(raw):
    if not raw:
        return ''
    value = str(raw).strip()
    if not value:
        return ''
    if _DRIVE_ID_RE.match(value):
        return value

    parsed = urlparse(value)
    if parsed.netloc:
        path_match = _DRIVE_FILE_PATH_RE.search(parsed.path)
        if path_match:
            return path_match.group(1)
        query = parse_qs(parsed.query)
        file_ids = query.get('id') or []
        if file_ids and _DRIVE_ID_RE.match(file_ids[0]):
            return file_ids[0]

    open_match = _DRIVE_OPEN_ID_RE.search(value)
    if open_match:
        return open_match.group(1)

    return value


def tour_fields_changed(instance):
    if not instance.pk:
        return bool(
            instance.tourPublished
            or instance.tourGoogleDriveFileId
            or instance.tourEntryUrl
        )

    old_published = getattr(instance, '_old_tour_published', None)
    old_file_id = getattr(instance, '_old_tour_google_drive_file_id', None)
    old_entry_url = getattr(instance, '_old_tour_entry_url', None)

    return (
        instance.tourPublished != old_published
        or instance.tourGoogleDriveFileId != old_file_id
        or instance.tourEntryUrl != old_entry_url
    )


def trigger_vercel_deploy():
    url = getattr(settings, 'VERCEL_DEPLOY_HOOK_URL', '') or ''
    if not url:
        logger.info('VERCEL_DEPLOY_HOOK_URL not set, skip deploy')
        return True
    try:
        response = requests.post(url, timeout=10)
        response.raise_for_status()
        return True
    except Exception:
        logger.exception('Vercel deploy hook failed')
        return False

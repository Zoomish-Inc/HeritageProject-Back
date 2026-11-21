import logging
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

_SLUG_RE = re.compile(r'^[A-Za-z0-9_-]+$')


class TourSyncError(Exception):
    pass


def sync_mode():
    return os.getenv('TOUR_SYNC_MODE', 'vercel').strip().lower() or 'vercel'


def tour_packs_root():
    raw = os.getenv('TOUR_PACKS_ROOT', '').strip()
    if not raw:
        return None
    return Path(raw)


def sync_object(instance):
    root = tour_packs_root()
    if root is None:
        raise TourSyncError('TOUR_PACKS_ROOT не задан.')

    slug = (instance.slug or '').strip()
    old_slug = (getattr(instance, '_old_slug', None) or '').strip()
    file_id = (instance.tourGoogleDriveFileId or '').strip()
    old_file_id = (getattr(instance, '_old_tour_google_drive_file_id', None) or '').strip()
    old_published = bool(getattr(instance, '_old_tour_published', None))

    if not instance.tourPublished:
        if slug:
            _remove_slug(root, slug)
        if old_slug and old_slug != slug:
            _remove_slug(root, old_slug)
        return

    _validate_slug(slug)
    if not file_id:
        raise TourSyncError('Для опубликованного тура нужен Google Drive file ID.')

    dest = root / slug
    same_slug = not old_slug or old_slug == slug
    if (
        old_published
        and same_slug
        and old_file_id == file_id
        and (dest / 'index.htm').is_file()
    ):
        return

    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=root) as tmp:
        zip_path = Path(tmp) / 'pack.zip'
        download_drive_zip(file_id, zip_path)
        install_tour_zip(root, slug, zip_path)

    if old_slug and old_slug != slug:
        _remove_slug(root, old_slug)


def sync_missing_published():
    from heritage.models import HeritageObject

    if sync_mode() != 'local':
        return 0

    root = tour_packs_root()
    if root is None:
        raise TourSyncError('TOUR_PACKS_ROOT не задан.')

    root.mkdir(parents=True, exist_ok=True)
    installed = 0
    queryset = HeritageObject.objects.filter(tourPublished=True).exclude(tourGoogleDriveFileId='')
    for obj in queryset.iterator():
        if not obj.slug or (root / obj.slug / 'index.htm').is_file():
            continue
        sync_object(obj)
        installed += 1
    return installed


def remove_tour_dir(slug):
    if sync_mode() != 'local' or not slug:
        return
    root = tour_packs_root()
    if root is None:
        return
    _remove_slug(root, slug)


def download_drive_zip(file_id, dest_path):
    url = (
        'https://drive.usercontent.google.com/download'
        f'?id={file_id}&export=download&confirm=t'
    )
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, timeout=180, stream=True, allow_redirects=True) as response:
        response.raise_for_status()
        content_type = (response.headers.get('Content-Type') or '').lower()
        with dest_path.open('wb') as handle:
            for chunk in response.iter_content(chunk_size=256 * 1024):
                if chunk:
                    handle.write(chunk)

    head = dest_path.read_bytes()[:200].lstrip().lower()
    if 'text/html' in content_type or head.startswith(b'<!doctype') or head.startswith(b'<html'):
        dest_path.unlink(missing_ok=True)
        raise TourSyncError(
            'Google Drive вернул страницу вместо zip. '
            'Проверьте доступ «Все, у кого есть ссылка».'
        )
    if dest_path.read_bytes()[:2] != b'PK':
        dest_path.unlink(missing_ok=True)
        raise TourSyncError('Скачанный файл не похож на zip.')


def install_tour_zip(root, slug, zip_path):
    _validate_slug(slug)
    root = Path(root)
    with tempfile.TemporaryDirectory(dir=root) as tmp:
        extracted = Path(tmp) / 'extracted'
        extracted.mkdir()
        _extract_zip(zip_path, extracted)
        web_root = _find_web_root(extracted)
        if web_root is None:
            raise TourSyncError('В архиве нет index.htm.')
        if not (web_root / 'lib' / 'tdvplayer.js').is_file():
            raise TourSyncError('В архиве нет lib/tdvplayer.js. Нужен полный экспорт 3DVista.')
        staging = root / f'.{slug}.new'
        if staging.exists():
            shutil.rmtree(staging)
        shutil.copytree(web_root, staging)
        _chmod_tree(staging)
        dest = root / slug
        if dest.exists():
            shutil.rmtree(dest)
        staging.rename(dest)


def _extract_zip(zip_path, destination):
    with zipfile.ZipFile(zip_path) as archive:
        for info in archive.infolist():
            if _is_unsafe(info.filename):
                raise TourSyncError('В архиве небезопасный путь.')
        for info in archive.infolist():
            target = destination / info.filename
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as source, target.open('wb') as handle:
                shutil.copyfileobj(source, handle)


def _is_unsafe(name):
    normalized = name.replace('\\', '/')
    if normalized.startswith('/') or ':' in normalized:
        return True
    parts = [part for part in normalized.split('/') if part not in ('', '.')]
    return any(part == '..' for part in parts)


def _find_web_root(directory):
    if (directory / 'index.htm').is_file():
        return directory
    for child in directory.iterdir():
        if child.is_dir():
            found = _find_web_root(child)
            if found is not None:
                return found
    return None


def _chmod_tree(path):
    os.chmod(path, 0o755)
    for dirpath, dirnames, filenames in os.walk(path):
        os.chmod(dirpath, 0o755)
        for name in filenames:
            os.chmod(os.path.join(dirpath, name), 0o644)


def _validate_slug(slug):
    if not slug or not _SLUG_RE.fullmatch(slug):
        raise TourSyncError('Некорректный slug тура.')


def _remove_slug(root, slug):
    _validate_slug(slug)
    root_resolved = Path(root).resolve()
    target = (root_resolved / slug).resolve()
    if root_resolved not in target.parents:
        raise TourSyncError('Некорректный путь тура.')
    if target.is_dir():
        shutil.rmtree(target)

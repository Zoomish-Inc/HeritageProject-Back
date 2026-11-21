import io
import json
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from django.forms.models import modelform_factory
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings

from heritage.http_cache import apply_public_cache_headers, compute_etag, not_modified_if_etag_matches
from heritage.middleware import PublicApiRateLimitMiddleware
from heritage.models import HeritageObject, PhotoItem
from heritage.tour_sync import TourSyncError, install_tour_zip, sync_object
from rest_framework.response import Response


class PhotoItemYearTests(TestCase):
    def test_save_without_year(self):
        heritage = HeritageObject.objects.create(name_ru='Мужская гимназия', slug='gymnasium')
        form_class = modelform_factory(PhotoItem, fields=['url', 'year'])
        form = form_class(
            data={
                'url': 'https://thumb.cloud.mail.ru/weblink/thumb/xw1/Mo41/BihcnaP57',
                'year': '',
            },
            instance=PhotoItem(heritage=heritage),
        )
        self.assertTrue(form.is_valid(), form.errors)
        photo = form.save()
        photo.refresh_from_db()
        self.assertIsNone(photo.year)


class PublishedListTests(TestCase):
    def test_list_returns_more_than_six_published(self):
        for index in range(7):
            HeritageObject.objects.create(
                name_ru=f'object {index}',
                slug=f'object-{index}',
                isPublished=True,
                order=index,
            )
        response = self.client.get('/api/v1/heritage/')
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(len(payload['data']), 7)


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



def _tour_zip(entries):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, payload in entries:
            archive.writestr(name, payload)
    return buffer.getvalue()


class TourPackSyncTests(SimpleTestCase):
    def test_extracts_nested_web_root(self):
        payload = _tour_zip([
            ("Web/index.htm", "<html></html>"),
            ("Web/lib/tdvplayer.js", "player"),
        ])
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            zip_path = root / "pack.zip"
            zip_path.write_bytes(payload)
            install_tour_zip(root, "chapel", zip_path)
            self.assertEqual((root / "chapel" / "index.htm").read_text(encoding="utf-8"), "<html></html>")
            self.assertTrue((root / "chapel" / "lib" / "tdvplayer.js").is_file())

    def test_rejects_parent_path(self):
        payload = _tour_zip([
            ("../index.htm", "x"),
            ("index.htm", "<html></html>"),
            ("lib/tdvplayer.js", "player"),
        ])
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            zip_path = root / "pack.zip"
            zip_path.write_bytes(payload)
            with self.assertRaises(TourSyncError):
                install_tour_zip(root, "chapel", zip_path)
            self.assertFalse((root / "chapel").exists())

    def test_unpublish_removes_directory(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "chapel"
            pack.mkdir()
            (pack / "index.htm").write_text("old", encoding="utf-8")
            obj = SimpleNamespace(
                slug="chapel",
                tourPublished=False,
                tourGoogleDriveFileId="file-id",
                _old_slug="chapel",
                _old_tour_published=True,
                _old_tour_google_drive_file_id="file-id",
            )
            with patch.dict("os.environ", {"TOUR_PACKS_ROOT": str(root)}):
                sync_object(obj)
            self.assertFalse(pack.exists())

    def test_skips_download_when_already_installed(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root / "chapel"
            (pack / "lib").mkdir(parents=True)
            (pack / "index.htm").write_text("ready", encoding="utf-8")
            obj = SimpleNamespace(
                slug="chapel",
                tourPublished=True,
                tourGoogleDriveFileId="file-id",
                _old_slug="chapel",
                _old_tour_published=True,
                _old_tour_google_drive_file_id="file-id",
            )
            with patch.dict("os.environ", {"TOUR_PACKS_ROOT": str(root)}):
                with patch("heritage.tour_sync.download_drive_zip") as download:
                    sync_object(obj)
            download.assert_not_called()
            self.assertEqual((pack / "index.htm").read_text(encoding="utf-8"), "ready")



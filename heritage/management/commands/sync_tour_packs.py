from django.core.management.base import BaseCommand

from heritage.tour_sync import TourSyncError, sync_missing_published, sync_mode


class Command(BaseCommand):
    help = 'Download published tour packs that are missing on disk.'

    def handle(self, *args, **options):
        if sync_mode() != 'local':
            self.stdout.write('TOUR_SYNC_MODE is not local, skip.')
            return
        try:
            installed = sync_missing_published()
        except TourSyncError as exc:
            self.stderr.write(str(exc))
            raise SystemExit(1) from exc
        self.stdout.write(f'Tour packs installed: {installed}')

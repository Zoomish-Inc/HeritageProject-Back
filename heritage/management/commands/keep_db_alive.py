from django.core.management.base import BaseCommand
from django.utils import timezone

from heritage.db_keepalive import ping_database


class Command(BaseCommand):
    help = 'Generate light read/write load to keep PostgreSQL awake on free tier.'

    def handle(self, *args, **options):
        stats = ping_database()
        self.stdout.write(
            self.style.SUCCESS(
                f'keepalive ok at {timezone.now().isoformat()}: '
                f'pings={stats["ping_count"]} '
                f'heritage={stats["heritage_published"]}/{stats["heritage_total"]}'
            )
        )

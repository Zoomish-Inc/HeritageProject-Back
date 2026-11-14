import os
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Создаёт суперпользователя, если он не существует.'

    def handle(self, *args, **options):
        if os.environ.get('CREATE_SUPERUSER', 'true').lower() in ('false', '0', 'no'):
            self.stdout.write('CREATE_SUPERUSER=False, пропускаем.')
            return

        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '').strip()
        if not password:
            self.stdout.write('DJANGO_SUPERUSER_PASSWORD is not set, skip superuser.')
            return

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username=os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin'),
                password=password,
                email=os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com'),
            )
            self.stdout.write('Суперпользователь создан.')
        else:
            self.stdout.write('Суперпользователь уже существует.')

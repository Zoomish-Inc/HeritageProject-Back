import os
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Создаёт суперпользователя, если он не существует.'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username=os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin'),
                password=os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'changeme123'),
                email=os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com'),
            )
            print('Суперпользователь создан.')
        else:
            print('Суперпользователь уже существует.')
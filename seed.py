import os
import sys

print(
    'seed.py устарел. Используйте: python manage.py seed_mock_heritage',
    file=sys.stderr,
)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django

django.setup()

from django.core.management import call_command

call_command('seed_mock_heritage', *sys.argv[1:])

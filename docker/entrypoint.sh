#!/bin/sh
set -eu

python manage.py migrate --noinput
python manage.py createsu
python manage.py setup_admin_roles
python manage.py sync_tour_packs

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 180

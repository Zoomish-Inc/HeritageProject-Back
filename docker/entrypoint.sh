#!/bin/sh
set -eu

python manage.py migrate --noinput
python manage.py createsu
python manage.py setup_admin_roles

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2

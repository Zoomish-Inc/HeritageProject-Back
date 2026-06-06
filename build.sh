#!/usr/bin/env bash

set -o errexit  # выход при ошибке

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py createsu
if [ "${SEED_MOCK_HERITAGE:-true}" != "false" ]; then
  python manage.py seed_mock_heritage
fi
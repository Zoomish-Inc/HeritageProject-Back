#!/usr/bin/env bash

set -o errexit  # выход при ошибке

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py createsu  # команда создания суперпользователя
python manage.py seed_mock_heritage  # TODO: удалить после первого деплоя с данными
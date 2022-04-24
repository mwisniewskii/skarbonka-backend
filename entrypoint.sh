#!/bin/bash

poetry run python manage.py migrate
poetry run python manage.py collectstatic --noinput
poetry run gunicorn project.wsgi:application --timeout 300 --bind 0.0.0.0:8000 --reload --access-logfile '-' --error-logfile '-'

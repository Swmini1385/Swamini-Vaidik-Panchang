#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
playwright install chromium
python manage.py migrate
python manage.py collectstatic --noinput

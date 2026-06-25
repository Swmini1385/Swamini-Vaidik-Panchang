#!/usr/bin/env bash
# exit on error
set -o errexit

export PLAYWRIGHT_BROWSERS_PATH=0
pip install -r requirements.txt
playwright install chromium
python manage.py collectstatic --noinput
python manage.py migrate

#!/bin/bash

set -e

echo "[*] Applying database migrations..."
python manage.py migrate --noinput

echo "[*] Starting Gunicorn WSGI server..."

exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3

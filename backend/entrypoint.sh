#!/bin/sh
set -e

echo "======================================"
echo "  CLinks.uz Backend ishga tushmoqda"
echo "======================================"

echo "[1/4] Migratsiyalar bajarilmoqda..."
python manage.py migrate --noinput

echo "[2/4] Static fayllar yig'ilmoqda..."
python manage.py collectstatic --noinput

echo "[3/4] Boshlang'ich ma'lumotlar tekshirilmoqda..."
python manage.py setup_initial_data --with-demo

echo "[4/4] Gunicorn server ishga tushmoqda..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -

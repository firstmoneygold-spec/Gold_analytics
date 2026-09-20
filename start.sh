#!/usr/bin/env bash
# Runtime entrypoint script for Render & cloud deployment
set -o errexit

echo "🗄️ Running database migrations on runtime container..."
python manage.py migrate --no-input

echo "🌱 Seeding default assets and physical gold catalogue..."
python manage.py shell -c "from apps.market_data.services.seeder import seed_default_assets; seed_default_assets()" || true

echo "🚀 Starting Gunicorn WSGI Server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}

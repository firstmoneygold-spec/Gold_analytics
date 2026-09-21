#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "📦 Installing project dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🎨 Collecting static assets with WhiteNoise..."
python manage.py collectstatic --no-input --settings=config.settings.production

echo "🗄️ Applying database migrations..."
python manage.py migrate --settings=config.settings.production

echo "🌟 Initializing baseline market assets and demo user accounts..."
python manage.py shell --settings=config.settings.production -c "from apps.market_data.services.seeder import seed_default_assets; seed_default_assets()" || true
python manage.py create_demo_trader --settings=config.settings.production || true

echo "✅ Build completed successfully!"

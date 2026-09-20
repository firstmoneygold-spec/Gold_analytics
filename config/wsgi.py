"""
WSGI config for TrendMaster AI project.
"""
import os
import sys
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
application = get_wsgi_application()

# 🚀 Automatic Database Migration & Seeder on Startup (Zero-Config for Free Cloud Dynos)
try:
    from django.core.management import call_command
    print("🗄️ Auto-running database migrations on startup...")
    call_command('migrate', interactive=False)
    
    from apps.market_data.services.seeder import seed_default_assets
    seed_default_assets()
    print("✅ Startup migrations and market assets initialized successfully!")
except Exception as e:
    print(f"ℹ️ Startup auto-migration status: {e}", file=sys.stderr)

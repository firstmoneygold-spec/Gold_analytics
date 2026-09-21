"""
WSGI config for TrendMaster AI project.
"""
import os
import sys
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
application = get_wsgi_application()

# 🚀 Automatic Database Migration, Seeder & Demo User Accounts Creation on Startup
try:
    from django.core.management import call_command
    print("🗄️ Auto-running database migrations on startup...")
    call_command('migrate', interactive=False)
    
    from apps.market_data.services.seeder import seed_default_assets
    seed_default_assets()

    # Automatically create / reset demo admin and pro trader accounts
    call_command('create_demo_trader')
    print("✅ Startup migrations, market assets, and demo user accounts initialized successfully!")
except Exception as e:
    print(f"ℹ️ Startup auto-initialization status: {e}", file=sys.stderr)

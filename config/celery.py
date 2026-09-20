"""
Celery configuration for TrendMaster AI.
"""
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

try:
    from celery import Celery
    app = Celery('trendmaster_ai')
    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.autodiscover_tasks()
except ImportError:
    app = None

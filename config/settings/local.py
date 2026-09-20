"""
Local development settings for TrendMaster AI.
"""
from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY', default='django-insecure-dev-key-trendmaster-ai-2026')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', default=True)

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['127.0.0.1', 'localhost', '0.0.0.0'])

# Database (SQLite by default for local development, easily switchable to PostgreSQL)
DATABASES = {
    'default': env.db('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}')
}

# In local dev, use simple file or console email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Celery local settings
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://127.0.0.1:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Payment Gateways (Test Mode)
STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY', default='pk_test_mock')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default='sk_test_mock')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET', default='whsec_mock')

RAZORPAY_KEY_ID = env('RAZORPAY_KEY_ID', default='rzp_test_mock')
RAZORPAY_KEY_SECRET = env('RAZORPAY_KEY_SECRET', default='rzp_secret_mock')

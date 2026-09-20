"""
URL configuration for TrendMaster AI project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core Application Routes
    path('', include('apps.dashboard.urls', namespace='dashboard')),
    path('auth/', include('apps.users.urls', namespace='users')),
    path('api/market/', include('apps.market_data.urls', namespace='market_data')),
    path('api/prediction/', include('apps.ai_engine.urls', namespace='ai_engine')),
    path('billing/', include('apps.billing.urls', namespace='billing')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

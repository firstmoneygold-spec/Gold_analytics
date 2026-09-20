from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Web UI Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('switch-market/', views.switch_market_preference, name='switch_market'),

    # REST API Authentication & Profile Endpoints
    path('api/register/', views.RegisterAPIView.as_view(), name='api_register'),
    path('api/login/', views.LoginAPIView.as_view(), name='api_login'),
    path('api/profile/', views.UserProfileAPIView.as_view(), name='api_profile'),
]

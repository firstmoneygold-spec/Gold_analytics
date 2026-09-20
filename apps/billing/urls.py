from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('pricing/', views.pricing_view, name='pricing'),
    path('checkout/', views.create_checkout_session, name='checkout'),
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('webhooks/razorpay/', views.razorpay_webhook, name='razorpay_webhook'),
]

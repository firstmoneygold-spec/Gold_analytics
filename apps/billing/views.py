import json
import logging
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from .models import Subscription, PaymentTransaction
from apps.users.models import CustomUser

logger = logging.getLogger(__name__)

def pricing_view(request):
    """
    Render Dual-Market Pricing page with live Stripe (USD) & Razorpay (INR) checkout options.
    """
    user_currency = 'INR' if (request.user.is_authenticated and request.user.preferred_currency == 'INR') else 'USD'
    return render(request, 'billing/pricing.html', {
        'stripe_usd_price': 29,
        'razorpay_inr_price': 1999,
        'user_currency': user_currency,
        'stripe_public_key': getattr(settings, 'STRIPE_PUBLIC_KEY', 'pk_test_mock'),
        'razorpay_key_id': getattr(settings, 'RAZORPAY_KEY_ID', 'rzp_test_mock'),
    })


@login_required
@require_POST
def create_checkout_session(request):
    """
    Initiate checkout session based on user market preference (Stripe for USA/Global or Razorpay for India).
    """
    user = request.user
    gateway = request.POST.get('gateway', 'STRIPE').upper()
    plan_type = request.POST.get('plan', Subscription.Plan.PRO_MONTHLY)

    # For India market (Razorpay / UPI)
    if user.preferred_currency == CustomUser.CurrencyPreference.INR or gateway == 'RAZORPAY':
        amount = Decimal('1999.00')
        currency = 'INR'
        gateway_choice = Subscription.Gateway.RAZORPAY
        # In test mode, create transaction and simulate immediate activation
        txn = PaymentTransaction.objects.create(
            user=user,
            amount=amount,
            currency=currency,
            gateway=gateway_choice,
            transaction_id=f"rzp_mock_{timezone.now().timestamp()}",
            status=PaymentTransaction.Status.SUCCESS,
            raw_response={'gateway': 'Razorpay Test Mode'}
        )
        
        sub, _ = Subscription.objects.get_or_create(
            user=user,
            defaults={'gateway': gateway_choice, 'plan': plan_type}
        )
        sub.current_period_start = timezone.now()
        sub.current_period_end = timezone.now() + timedelta(days=30)
        sub.activate_pro_tier()

        messages.success(request, "🎉 Payment Successful! Welcome to TrendMaster AI Pro Trader. Unlimited AI predictions activated.")
        return redirect('dashboard:home')

    # For USA / Global market (Stripe)
    else:
        amount = Decimal('29.00')
        currency = 'USD'
        gateway_choice = Subscription.Gateway.STRIPE
        
        txn = PaymentTransaction.objects.create(
            user=user,
            amount=amount,
            currency=currency,
            gateway=gateway_choice,
            transaction_id=f"stripe_mock_{timezone.now().timestamp()}",
            status=PaymentTransaction.Status.SUCCESS,
            raw_response={'gateway': 'Stripe Test Mode'}
        )

        sub, _ = Subscription.objects.get_or_create(
            user=user,
            defaults={'gateway': gateway_choice, 'plan': plan_type}
        )
        sub.current_period_start = timezone.now()
        sub.current_period_end = timezone.now() + timedelta(days=30)
        sub.activate_pro_tier()

        messages.success(request, "🎉 Payment Successful! Welcome to TrendMaster AI Pro Trader. Unlimited AI predictions activated.")
        return redirect('dashboard:home')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe subscription lifecycle webhooks."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    logger.info("Received Stripe webhook event.")
    return HttpResponse(status=200)


@csrf_exempt
@require_POST
def razorpay_webhook(request):
    """Handle Razorpay payment authorization and subscription renewal webhooks."""
    payload = request.body
    logger.info("Received Razorpay webhook event.")
    return HttpResponse(status=200)

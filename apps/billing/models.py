from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Subscription(models.Model):
    """
    User SaaS Subscription Record across Stripe (USA/Global) and Razorpay (India).
    """
    class Gateway(models.TextChoices):
        STRIPE = 'STRIPE', _('Stripe (USD / Global)')
        RAZORPAY = 'RAZORPAY', _('Razorpay (INR / India)')
        MANUAL = 'MANUAL', _('Admin Assigned')

    class Plan(models.TextChoices):
        PRO_MONTHLY = 'PRO_MONTHLY', _('Pro Trader Monthly')
        PRO_YEARLY = 'PRO_YEARLY', _('Pro Trader Yearly')
        ENTERPRISE = 'ENTERPRISE', _('Enterprise / Institutional')

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', _('Active')
        CANCELED = 'CANCELED', _('Canceled')
        PAST_DUE = 'PAST_DUE', _('Past Due')
        EXPIRED = 'EXPIRED', _('Expired')

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    gateway = models.CharField(max_length=20, choices=Gateway.choices, default=Gateway.STRIPE)
    plan = models.CharField(max_length=20, choices=Plan.choices, default=Plan.PRO_MONTHLY)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    
    gateway_customer_id = models.CharField(max_length=100, blank=True, null=True)
    gateway_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.plan} ({self.status})"

    def activate_pro_tier(self):
        self.status = self.Status.ACTIVE
        self.save()
        self.user.subscription_tier = self.user.SubscriptionTier.PRO
        self.user.save(update_fields=['subscription_tier'])


class PaymentTransaction(models.Model):
    """
    Audit ledger of all payment transactions and checkout sessions.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        SUCCESS = 'SUCCESS', _('Success')
        FAILED = 'FAILED', _('Failed')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=5, default='USD')
    gateway = models.CharField(max_length=20, choices=Subscription.Gateway.choices, default=Subscription.Gateway.STRIPE)
    transaction_id = models.CharField(max_length=150, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    raw_response = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.currency} {self.amount} ({self.status})"

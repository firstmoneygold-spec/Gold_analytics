from django.contrib import admin
from .models import Subscription, PaymentTransaction

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'gateway', 'status', 'current_period_end', 'updated_at')
    list_filter = ('gateway', 'plan', 'status')
    search_fields = ('user__email', 'gateway_subscription_id')


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'currency', 'gateway', 'status', 'transaction_id', 'created_at')
    list_filter = ('gateway', 'status', 'currency')
    search_fields = ('user__email', 'transaction_id')

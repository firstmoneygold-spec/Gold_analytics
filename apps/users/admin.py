from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'full_name', 'subscription_tier', 'preferred_market', 'preferred_currency', 'credits_remaining', 'is_staff', 'is_active')
    list_filter = ('subscription_tier', 'preferred_market', 'preferred_currency', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'phone_number', 'telegram_chat_id', 'whatsapp_number')}),
        ('Market Preferences', {'fields': ('preferred_market', 'preferred_currency', 'preferred_gold_unit')}),
        ('SaaS Subscription & Quota', {'fields': ('subscription_tier', 'credits_remaining', 'predictions_used_today', 'last_prediction_date', 'is_verified')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('email',)
    search_fields = ('email', 'full_name')

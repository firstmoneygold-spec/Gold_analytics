from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """Custom user manager where email is the unique identifier for auth."""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('subscription_tier', 'ENTERPRISE')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    SaaS User Model with Dual-Market (USA & India) Preferences and Subscription Tier Gating.
    """
    class SubscriptionTier(models.TextChoices):
        FREE = 'FREE', _('Free Explorer (3 Predictions/Day)')
        PRO = 'PRO', _('Pro Trader (Unlimited + Signals)')
        ENTERPRISE = 'ENTERPRISE', _('Institutional / Enterprise API')

    class MarketPreference(models.TextChoices):
        INDIA = 'INDIA', _('India (NSE / BSE / MCX)')
        USA = 'USA', _('USA (NYSE / NASDAQ / COMEX)')
        GLOBAL = 'GLOBAL', _('Global All-Markets')

    class CurrencyPreference(models.TextChoices):
        INR = 'INR', _('INR (₹) - Indian Rupee')
        USD = 'USD', _('USD ($) - US Dollar')

    class GoldUnitPreference(models.TextChoices):
        TEN_GRAMS = '10g', _('10 Grams (India MCX / Retail)')
        TROY_OUNCE = 'oz', _('Troy Ounce (US COMEX / Global Spot)')

    username = None
    email = models.EmailField(_('email address'), unique=True)
    full_name = models.CharField(_('full name'), max_length=150, blank=True)
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True)
    
    # Regional & Market Preferences
    preferred_market = models.CharField(
        max_length=10, 
        choices=MarketPreference.choices, 
        default=MarketPreference.INDIA
    )
    preferred_currency = models.CharField(
        max_length=5, 
        choices=CurrencyPreference.choices, 
        default=CurrencyPreference.INR
    )
    preferred_gold_unit = models.CharField(
        max_length=5, 
        choices=GoldUnitPreference.choices, 
        default=GoldUnitPreference.TEN_GRAMS
    )

    # SaaS Access & Credits
    subscription_tier = models.CharField(
        max_length=15, 
        choices=SubscriptionTier.choices, 
        default=SubscriptionTier.FREE
    )
    is_verified = models.BooleanField(default=True)
    credits_remaining = models.IntegerField(default=10)
    predictions_used_today = models.IntegerField(default=0)
    last_prediction_date = models.DateField(null=True, blank=True)

    # External Integrations for Alerts
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.subscription_tier})"

    @property
    def is_pro_or_higher(self):
        return self.subscription_tier in [self.SubscriptionTier.PRO, self.SubscriptionTier.ENTERPRISE]

    def reset_daily_quota_if_needed(self):
        """Reset daily predictions count if a new day has started."""
        today = timezone.now().date()
        if self.last_prediction_date != today:
            self.predictions_used_today = 0
            self.last_prediction_date = today
            self.save(update_fields=['predictions_used_today', 'last_prediction_date'])

    def can_make_prediction(self):
        """Check if user has remaining quota or credits for prediction."""
        if self.is_pro_or_higher:
            return True, "Unlimited Pro Access"
        
        self.reset_daily_quota_if_needed()
        if self.predictions_used_today < 3:
            return True, f"{3 - self.predictions_used_today} free predictions remaining today"
        
        if self.credits_remaining > 0:
            return True, f"{self.credits_remaining} prepaid credits remaining"
            
        return False, "Daily limit reached. Upgrade to Pro Trader for unlimited AI predictions."

    def deduct_prediction_usage(self):
        """Deduct prediction usage from daily limit or credits."""
        if self.is_pro_or_higher:
            return True
        
        self.reset_daily_quota_if_needed()
        if self.predictions_used_today < 3:
            self.predictions_used_today += 1
            self.save(update_fields=['predictions_used_today'])
            return True
        elif self.credits_remaining > 0:
            self.credits_remaining -= 1
            self.save(update_fields=['credits_remaining'])
            return True
        return False

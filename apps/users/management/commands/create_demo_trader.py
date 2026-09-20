from django.core.management.base import BaseCommand
from apps.users.models import CustomUser

class Command(BaseCommand):
    help = 'Create default demo trader and admin accounts'

    def handle(self, *args, **options):
        # 1. Pro Trader Account
        pro_user, created = CustomUser.objects.get_or_create(
            email='trader@trendmaster.ai',
            defaults={
                'full_name': 'Pro Trader',
                'preferred_market': CustomUser.MarketPreference.INDIA,
                'preferred_currency': CustomUser.CurrencyPreference.INR,
                'preferred_gold_unit': CustomUser.GoldUnitPreference.TEN_GRAMS,
                'subscription_tier': CustomUser.SubscriptionTier.PRO,
                'credits_remaining': 500,
                'is_verified': True
            }
        )
        pro_user.set_password('GoldTrader2026!')
        pro_user.save()

        # 2. Superuser Admin Account
        admin_user, created_admin = CustomUser.objects.get_or_create(
            email='admin@trendmaster.ai',
            defaults={
                'full_name': 'System Administrator',
                'preferred_market': CustomUser.MarketPreference.USA,
                'preferred_currency': CustomUser.CurrencyPreference.USD,
                'subscription_tier': CustomUser.SubscriptionTier.ENTERPRISE,
                'is_staff': True,
                'is_superuser': True,
                'is_verified': True
            }
        )
        admin_user.set_password('AdminMaster2026!')
        admin_user.save()

        self.stdout.write(self.style.SUCCESS('Successfully configured demo accounts:'))
        self.stdout.write(self.style.SUCCESS('  Pro Trader -> Email: trader@trendmaster.ai | Pass: GoldTrader2026!'))
        self.stdout.write(self.style.SUCCESS('  Admin User -> Email: admin@trendmaster.ai  | Pass: AdminMaster2026!'))

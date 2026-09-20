from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import CustomUser

class UserAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.api_client = APIClient()
        self.user_data = {
            'email': 'trader_india@example.com',
            'password': 'StrongPassword123!',
            'full_name': 'Rajesh Sharma',
            'preferred_market': 'INDIA',
            'preferred_currency': 'INR',
            'preferred_gold_unit': '10g'
        }

    def test_user_creation_and_quota(self):
        """Test user creation and daily quota calculation."""
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertEqual(user.email, 'trader_india@example.com')
        self.assertEqual(user.subscription_tier, CustomUser.SubscriptionTier.FREE)
        self.assertEqual(user.preferred_market, 'INDIA')
        
        can_predict, msg = user.can_make_prediction()
        self.assertTrue(can_predict)
        self.assertIn("3 free predictions", msg)

        # Deduct 3 predictions
        for _ in range(3):
            self.assertTrue(user.deduct_prediction_usage())

        # 4th prediction should fail on free tier
        user.credits_remaining = 0
        user.save()
        can_predict_4th, _ = user.can_make_prediction()
        self.assertFalse(can_predict_4th)

    def test_web_registration_and_login(self):
        """Test registration and login flow via web views."""
        reg_response = self.client.post(reverse('users:register'), {
            'email': 'newtrader@example.com',
            'full_name': 'New Trader',
            'preferred_market': 'USA',
            'preferred_currency': 'USD',
            'preferred_gold_unit': 'oz',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!',
        })
        self.assertEqual(reg_response.status_code, 302)

        # Check login
        login_response = self.client.post(reverse('users:login'), {
            'email': 'newtrader@example.com',
            'password': 'SecurePassword123!',
        })
        self.assertEqual(login_response.status_code, 302)

    def test_api_registration_and_jwt_token(self):
        """Test REST API registration and token generation."""
        response = self.api_client.post(reverse('users:api_register'), {
            'email': 'apitrader@example.com',
            'password': 'ApiSecurePass123!',
            'full_name': 'API Trader',
            'preferred_market': 'USA',
            'preferred_currency': 'USD',
            'preferred_gold_unit': 'oz'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['preferred_market'], 'USA')

    def test_market_switching_ajax(self):
        """Test AJAX market switcher."""
        user = CustomUser.objects.create_user(**self.user_data)
        self.client.force_login(user)

        response = self.client.post(reverse('users:switch_market'), {'market': 'USA'})
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.preferred_market, 'USA')
        self.assertEqual(user.preferred_currency, 'USD')
        self.assertEqual(user.preferred_gold_unit, 'oz')

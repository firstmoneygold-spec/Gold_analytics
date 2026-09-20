from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from apps.users.models import CustomUser
from apps.market_data.models import Asset, HistoricalPrice
from apps.ai_engine.models import PredictionRecord, AccuracyAudit
from apps.ai_engine.models_ml.predictor import generate_ai_prediction
from apps.ai_engine.models_ml.scenario_simulator import simulate_macro_scenario

class AiEngineTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email='gold_trader@example.com',
            password='TestPassword123!',
            full_name='Gold Trader',
            preferred_market='INDIA',
            preferred_currency='INR',
            credits_remaining=5
        )

        self.gold_asset = Asset.objects.create(
            symbol='GC=F',
            name='Gold COMEX Futures',
            asset_type=Asset.AssetType.COMMODITY,
            market=Asset.Market.USA,
            currency=Asset.Currency.USD,
            display_unit='oz',
            last_price=Decimal('2350.00'),
            is_active=True
        )

        # Create 35 historical daily bars for testing
        now = timezone.now()
        prices = []
        for i in range(35):
            ts = now - timedelta(days=35 - i)
            base_p = 2300.0 + (i * 2.0)
            prices.append(
                HistoricalPrice(
                    asset=self.gold_asset,
                    timestamp=ts,
                    timeframe=HistoricalPrice.Timeframe.DAY_1,
                    open=Decimal(str(base_p - 1.0)),
                    high=Decimal(str(base_p + 5.0)),
                    low=Decimal(str(base_p - 3.0)),
                    close=Decimal(str(base_p + 2.0)),
                    volume=15000 + (i * 100)
                )
            )
        HistoricalPrice.objects.bulk_create(prices)

    def test_prediction_generation(self):
        """Test AI prediction generation with target corridors and stop loss."""
        prediction = generate_ai_prediction(
            asset=self.gold_asset,
            timeframe=HistoricalPrice.Timeframe.DAY_1,
            horizon_days=7,
            user=self.user
        )

        self.assertIsNotNone(prediction)
        self.assertIn(prediction.signal, [s[0] for s in PredictionRecord.SignalType.choices])
        self.assertGreaterEqual(prediction.confidence_score, 80.0)
        self.assertGreater(prediction.expected_target_price, 0)
        self.assertGreater(prediction.stop_loss, 0)
        self.assertGreater(prediction.take_profit_1, 0)
        self.assertEqual(prediction.user, self.user)

    def test_forecast_api_with_authentication(self):
        """Test forecast API endpoint requiring authentication."""
        # Unauthenticated request should fail (401 or 403)
        url = reverse('ai_engine:generate_forecast', kwargs={'symbol': 'GC=F'})
        res_unauth = self.client.post(url, {})
        self.assertIn(res_unauth.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        # Authenticated request succeeds
        self.client.force_authenticate(user=self.user)
        res_auth = self.client.post(url, {'timeframe': '1d', 'horizon_days': 7}, format='json')
        self.assertEqual(res_auth.status_code, status.HTTP_201_CREATED)
        self.assertIn('prediction', res_auth.data)
        self.assertEqual(res_auth.data['prediction']['asset_symbol'], 'GC=F')

    def test_scenario_simulator(self):
        """Test What-If macro scenario simulations."""
        result = simulate_macro_scenario(
            asset=self.gold_asset,
            fed_rate_change_bps=-50.0,  # 50 bps cut
            dxy_change_pct=-1.5,        # 1.5% DXY drop
            crude_oil_change_pct=5.0    # 5% crude push
        )
        self.assertEqual(result['asset_symbol'], 'GC=F')
        self.assertEqual(result['direction'], 'BULLISH')
        self.assertGreater(result['simulated_price'], result['current_price'])

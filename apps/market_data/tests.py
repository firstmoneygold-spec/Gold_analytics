from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from decimal import Decimal

from apps.market_data.models import Asset, HistoricalPrice, MacroIndicator, FinancialNews
from apps.market_data.services.seeder import seed_default_assets
from apps.market_data.services.news_service import analyze_sentiment
from apps.market_data.services.yfinance_service import get_candles_for_chart

class MarketDataTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.gold_asset = Asset.objects.create(
            symbol='GC=F',
            name='Gold COMEX Futures',
            asset_type=Asset.AssetType.COMMODITY,
            market=Asset.Market.USA,
            currency=Asset.Currency.USD,
            display_unit='oz',
            last_price=Decimal('2350.50'),
            is_active=True
        )

        self.nifty_asset = Asset.objects.create(
            symbol='^NSEI',
            name='Nifty 50 Index',
            asset_type=Asset.AssetType.INDEX,
            market=Asset.Market.INDIA,
            currency=Asset.Currency.INR,
            display_unit='points',
            last_price=Decimal('24500.00'),
            is_active=True
        )

    def test_seeder_functionality(self):
        """Test default asset seeder populates USA & Indian assets."""
        created, total = seed_default_assets()
        self.assertGreaterEqual(total, 10)
        self.assertTrue(Asset.objects.filter(symbol='GOLDBEES.NS').exists())
        self.assertTrue(Asset.objects.filter(symbol='NVDA').exists())
        self.assertTrue(Asset.objects.filter(symbol='RELIANCE.NS').exists())

    def test_sentiment_analysis_logic(self):
        """Test financial NLP sentiment polarity calculation."""
        # Bullish headline
        score_bull, label_bull, conf_bull = analyze_sentiment("Gold rallies to all-time high as Fed hints rate cut")
        self.assertEqual(label_bull, FinancialNews.SentimentLabel.BULLISH)
        self.assertGreater(score_bull, 0.0)

        # Bearish headline
        score_bear, label_bear, conf_bear = analyze_sentiment("Stock market plunges on recession fears and inflation spike")
        self.assertEqual(label_bear, FinancialNews.SentimentLabel.BEARISH)
        self.assertLess(score_bear, 0.0)

    def test_candles_serialization_for_tradingview(self):
        """Test candlestick data format for TradingView charts."""
        now = timezone.now()
        HistoricalPrice.objects.create(
            asset=self.gold_asset,
            timestamp=now,
            timeframe=HistoricalPrice.Timeframe.DAY_1,
            open=Decimal('2340.0'),
            high=Decimal('2360.0'),
            low=Decimal('2335.0'),
            close=Decimal('2355.0'),
            volume=12000
        )

        candles = get_candles_for_chart(self.gold_asset, timeframe=HistoricalPrice.Timeframe.DAY_1)
        self.assertEqual(len(candles), 1)
        self.assertEqual(candles[0]['close'], 2355.0)
        self.assertIn('time', candles[0])

    def test_api_endpoints(self):
        """Test API endpoints for asset list, candles, macro, and news."""
        # Asset list API
        resp = self.client.get(reverse('market_data:asset_list'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data), 2)

        # Candles API
        candle_resp = self.client.get(reverse('market_data:chart_candles', kwargs={'symbol': 'GC=F'}))
        self.assertEqual(candle_resp.status_code, status.HTTP_200_OK)
        self.assertIn('candles', candle_resp.data)

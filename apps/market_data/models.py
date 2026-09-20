from django.db import models
from django.utils.translation import gettext_lazy as _

class Asset(models.Model):
    """
    Financial Asset (Commodities, Equities, Indices, Forex) across USA & Indian markets.
    """
    class AssetType(models.TextChoices):
        COMMODITY = 'COMMODITY', _('Commodity / Precious Metal')
        EQUITY = 'EQUITY', _('Equity / Stock')
        INDEX = 'INDEX', _('Market Index')
        FOREX = 'FOREX', _('Forex Currency Pair')

    class Market(models.TextChoices):
        USA = 'USA', _('United States (NYSE / NASDAQ / COMEX)')
        INDIA = 'INDIA', _('India (NSE / BSE / MCX)')
        GLOBAL = 'GLOBAL', _('Global 24/5 Market')

    class Currency(models.TextChoices):
        USD = 'USD', _('USD ($)')
        INR = 'INR', _('INR (₹)')

    symbol = models.CharField(max_length=30, unique=True, help_text="Ticker (e.g. GC=F, GLD, GOLDBEES.NS, NVDA, RELIANCE.NS, ^NSEI)")
    name = models.CharField(max_length=150)
    asset_type = models.CharField(max_length=20, choices=AssetType.choices, default=AssetType.COMMODITY)
    market = models.CharField(max_length=10, choices=Market.choices, default=Market.INDIA)
    currency = models.CharField(max_length=5, choices=Currency.choices, default=Currency.INR)
    display_unit = models.CharField(max_length=20, default='share', help_text="e.g. oz, 10g, share, points")
    
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text="Pinned on dashboard header")
    description = models.TextField(blank=True, null=True)
    
    last_price = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    price_change_24h = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_change_pct_24h = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', 'market', 'symbol']

    def __str__(self):
        return f"{self.symbol} - {self.name} ({self.market})"


class HistoricalPrice(models.Model):
    """
    Time-series OHLCV Candlestick bar for an asset.
    """
    class Timeframe(models.TextChoices):
        MIN_15 = '15m', _('15 Minutes')
        HOUR_1 = '1h', _('1 Hour')
        HOUR_4 = '4h', _('4 Hours')
        DAY_1 = '1d', _('1 Day')
        WEEK_1 = '1w', _('1 Week')
        MONTH_1 = '1M', _('1 Month')

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='historical_prices')
    timestamp = models.DateTimeField(db_index=True)
    timeframe = models.CharField(max_length=5, choices=Timeframe.choices, default=Timeframe.DAY_1)
    
    open = models.DecimalField(max_digits=14, decimal_places=4)
    high = models.DecimalField(max_digits=14, decimal_places=4)
    low = models.DecimalField(max_digits=14, decimal_places=4)
    close = models.DecimalField(max_digits=14, decimal_places=4)
    volume = models.BigIntegerField(default=0)

    class Meta:
        ordering = ['timestamp']
        unique_together = ('asset', 'timestamp', 'timeframe')
        indexes = [
            models.Index(fields=['asset', 'timeframe', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.asset.symbol} [{self.timeframe}] {self.timestamp.strftime('%Y-%m-%d %H:%M')}: {self.close}"


class MacroIndicator(models.Model):
    """
    Macroeconomic Drivers for Gold & Stock markets (USA & India).
    """
    code = models.CharField(max_length=30, db_index=True)
    name = models.CharField(max_length=150)
    market = models.CharField(max_length=10, choices=Asset.Market.choices, default=Asset.Market.GLOBAL)
    value = models.DecimalField(max_digits=12, decimal_places=4)
    change_pct = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    unit = models.CharField(max_length=20, default='%')
    date = models.DateField(db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'code']
        unique_together = ('code', 'date')

    def __str__(self):
        return f"{self.code} ({self.date}): {self.value} {self.unit}"


class FinancialNews(models.Model):
    """
    Real-time Financial & Commodity News with FinBERT Sentiment Scoring.
    """
    class SentimentLabel(models.TextChoices):
        BULLISH = 'BULLISH', _('Bullish / Positive')
        BEARISH = 'BEARISH', _('Bearish / Negative')
        NEUTRAL = 'NEUTRAL', _('Neutral')

    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, blank=True, related_name='news')
    market = models.CharField(max_length=10, choices=Asset.Market.choices, default=Asset.Market.GLOBAL)
    
    title = models.CharField(max_length=300)
    source = models.CharField(max_length=100)
    url = models.URLField(max_length=500, unique=True)
    published_at = models.DateTimeField(db_index=True)
    summary = models.TextField(blank=True, null=True)
    
    sentiment_score = models.FloatField(default=0.0, help_text="Polarity: -1.0 to +1.0")
    sentiment_label = models.CharField(max_length=10, choices=SentimentLabel.choices, default=SentimentLabel.NEUTRAL)
    sentiment_confidence = models.FloatField(default=0.5)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return f"[{self.sentiment_label} {self.sentiment_score:+.2f}] {self.title[:60]}"

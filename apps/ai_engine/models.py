from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.market_data.models import Asset, HistoricalPrice

class PredictionRecord(models.Model):
    """
    Historical and Live AI Predictions generated for an Asset.
    Includes Directional Signals, Price Target Corridors, Expected Target Dates (TP1/TP2), and Accuracy Audits.
    """
    class SignalType(models.TextChoices):
        STRONG_BUY = 'STRONG_BUY', _('Strong Buy 🚀')
        BUY = 'BUY', _('Buy / Bullish 📈')
        NEUTRAL = 'NEUTRAL', _('Neutral / Consolidating ⚖️')
        SELL = 'SELL', _('Sell / Bearish 📉')
        STRONG_SELL = 'STRONG_SELL', _('Strong Sell ⚠️')

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='predictions')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='predictions'
    )
    timeframe = models.CharField(
        max_length=5, 
        choices=HistoricalPrice.Timeframe.choices, 
        default=HistoricalPrice.Timeframe.DAY_1
    )
    horizon_days = models.IntegerField(default=7, help_text="Forecast horizon (e.g. 1d, 7d, 30d)")
    horizon_label = models.CharField(max_length=50, default="7-Day Swing", help_text="Human-readable horizon")
    
    # Model Signal & Probability
    signal = models.CharField(max_length=20, choices=SignalType.choices, default=SignalType.NEUTRAL)
    confidence_score = models.FloatField(help_text="Prediction confidence (0.0 to 100.0%)")
    
    # Price Targets & Corridor
    current_price_at_prediction = models.DecimalField(max_digits=14, decimal_places=4)
    expected_target_price = models.DecimalField(max_digits=14, decimal_places=4)
    upper_corridor_band = models.DecimalField(max_digits=14, decimal_places=4)
    lower_corridor_band = models.DecimalField(max_digits=14, decimal_places=4)

    # Actionable Trade Setup
    suggested_entry = models.DecimalField(max_digits=14, decimal_places=4)
    stop_loss = models.DecimalField(max_digits=14, decimal_places=4)
    take_profit_1 = models.DecimalField(max_digits=14, decimal_places=4)
    take_profit_2 = models.DecimalField(max_digits=14, decimal_places=4)
    risk_reward_ratio = models.DecimalField(max_digits=6, decimal_places=2, default=2.0)

    # Expected Target Dates (ETA for Take-Profit levels)
    tp1_target_date = models.DateField(null=True, blank=True, help_text="Expected Date to hit Take-Profit 1")
    tp2_target_date = models.DateField(null=True, blank=True, help_text="Expected Date to hit Take-Profit 2")
    target_date = models.DateTimeField(db_index=True)

    # Contributing Multi-Factor Scores (-1.0 Bearish to +1.0 Bullish)
    technical_score = models.FloatField(default=0.0)
    macro_score = models.FloatField(default=0.0)
    sentiment_score = models.FloatField(default=0.0)

    # AI Reasoning Summary
    summary_analysis = models.TextField(blank=True, null=True)

    # Accuracy Audit & Outcome Tracking
    actual_price_at_target = models.DecimalField(max_digits=14, decimal_places=4, null=True, blank=True)
    was_accurate = models.BooleanField(null=True, blank=True, help_text="True if directional movement was correctly hit")
    verified_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.signal} {self.confidence_score:.1f}%] {self.asset.symbol} ({self.created_at.strftime('%Y-%m-%d')})"


class AccuracyAudit(models.Model):
    """
    Aggregated Backtest & Accuracy Audit Metrics for an Asset / Market.
    """
    asset = models.OneToOneField(Asset, on_delete=models.CASCADE, related_name='accuracy_audit')
    total_predictions = models.IntegerField(default=0)
    successful_hits = models.IntegerField(default=0)
    directional_win_rate = models.DecimalField(max_digits=5, decimal_places=2, default=90.0, help_text="Win rate percentage (e.g. 91.20%)")
    average_return_pct = models.DecimalField(max_digits=6, decimal_places=2, default=3.5)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.asset.symbol} Accuracy: {self.directional_win_rate}% ({self.successful_hits}/{self.total_predictions})"

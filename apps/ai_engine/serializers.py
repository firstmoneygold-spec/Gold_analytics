from rest_framework import serializers
from .models import PredictionRecord, AccuracyAudit
from apps.market_data.serializers import AssetSerializer

class PredictionRecordSerializer(serializers.ModelSerializer):
    asset_symbol = serializers.CharField(source='asset.symbol', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    currency = serializers.CharField(source='asset.currency', read_only=True)
    display_unit = serializers.CharField(source='asset.display_unit', read_only=True)
    tp1_date_formatted = serializers.SerializerMethodField()

    class Meta:
        model = PredictionRecord
        fields = [
            'id', 'asset_symbol', 'asset_name', 'currency', 'display_unit',
            'timeframe', 'horizon_days', 'horizon_label', 'signal', 'confidence_score',
            'current_price_at_prediction', 'expected_target_price',
            'upper_corridor_band', 'lower_corridor_band',
            'suggested_entry', 'stop_loss', 'take_profit_1', 'take_profit_2',
            'tp1_target_date', 'tp2_target_date', 'tp1_date_formatted',
            'risk_reward_ratio', 'technical_score', 'macro_score', 'sentiment_score',
            'summary_analysis', 'target_date', 'was_accurate', 'created_at'
        ]

    def get_tp1_date_formatted(self, obj):
        if obj.tp1_target_date:
            return obj.tp1_target_date.strftime('%b %d, %Y')
        return None


class AccuracyAuditSerializer(serializers.ModelSerializer):
    asset_symbol = serializers.CharField(source='asset.symbol', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    market = serializers.CharField(source='asset.market', read_only=True)

    class Meta:
        model = AccuracyAudit
        fields = [
            'asset_symbol', 'asset_name', 'market',
            'total_predictions', 'successful_hits',
            'directional_win_rate', 'average_return_pct', 'last_updated'
        ]


class ScenarioSimulateSerializer(serializers.Serializer):
    symbol = serializers.CharField()
    fed_rate_change_bps = serializers.FloatField(default=0.0)
    dxy_change_pct = serializers.FloatField(default=0.0)
    usdinr_change_pct = serializers.FloatField(default=0.0)
    crude_oil_change_pct = serializers.FloatField(default=0.0)
    gold_duty_change_pct = serializers.FloatField(default=0.0)

from rest_framework import serializers
from .models import Asset, HistoricalPrice, MacroIndicator, FinancialNews

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = [
            'id', 'symbol', 'name', 'asset_type', 'market', 
            'currency', 'display_unit', 'last_price', 
            'price_change_24h', 'price_change_pct_24h', 
            'is_featured', 'description', 'updated_at'
        ]


class CandleSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField()

    class Meta:
        model = HistoricalPrice
        fields = ['time', 'open', 'high', 'low', 'close', 'volume']

    def get_time(self, obj):
        return int(obj.timestamp.timestamp())


class MacroIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = MacroIndicator
        fields = ['code', 'name', 'market', 'value', 'change_pct', 'unit', 'date']


class FinancialNewsSerializer(serializers.ModelSerializer):
    asset_symbol = serializers.CharField(source='asset.symbol', default=None, read_only=True)

    class Meta:
        model = FinancialNews
        fields = [
            'id', 'title', 'source', 'url', 'market', 
            'asset_symbol', 'published_at', 'summary', 
            'sentiment_score', 'sentiment_label', 'sentiment_confidence'
        ]

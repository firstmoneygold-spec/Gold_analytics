from django.contrib import admin
from .models import Asset, HistoricalPrice, MacroIndicator, FinancialNews

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'asset_type', 'market', 'currency', 'last_price', 'price_change_pct_24h', 'is_featured', 'is_active')
    list_filter = ('market', 'asset_type', 'currency', 'is_featured', 'is_active')
    search_fields = ('symbol', 'name')
    ordering = ('-is_featured', 'market', 'symbol')


@admin.register(HistoricalPrice)
class HistoricalPriceAdmin(admin.ModelAdmin):
    list_display = ('asset', 'timeframe', 'timestamp', 'open', 'high', 'low', 'close', 'volume')
    list_filter = ('timeframe', 'asset__market', 'asset__asset_type')
    search_fields = ('asset__symbol', 'asset__name')
    date_hierarchy = 'timestamp'


@admin.register(MacroIndicator)
class MacroIndicatorAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'market', 'value', 'unit', 'change_pct', 'date')
    list_filter = ('market', 'code')
    date_hierarchy = 'date'


@admin.register(FinancialNews)
class FinancialNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'market', 'asset', 'sentiment_label', 'sentiment_score', 'published_at')
    list_filter = ('market', 'sentiment_label', 'source')
    search_fields = ('title', 'summary', 'source')
    date_hierarchy = 'published_at'

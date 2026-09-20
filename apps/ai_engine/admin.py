from django.contrib import admin
from .models import PredictionRecord, AccuracyAudit

@admin.register(PredictionRecord)
class PredictionRecordAdmin(admin.ModelAdmin):
    list_display = ('asset', 'signal', 'confidence_score', 'current_price_at_prediction', 'expected_target_price', 'stop_loss', 'take_profit_1', 'was_accurate', 'created_at')
    list_filter = ('signal', 'timeframe', 'was_accurate', 'asset__market')
    search_fields = ('asset__symbol', 'asset__name', 'user__email')
    date_hierarchy = 'created_at'


@admin.register(AccuracyAudit)
class AccuracyAuditAdmin(admin.ModelAdmin):
    list_display = ('asset', 'directional_win_rate', 'successful_hits', 'total_predictions', 'average_return_pct', 'last_updated')
    list_filter = ('asset__market', 'asset__asset_type')

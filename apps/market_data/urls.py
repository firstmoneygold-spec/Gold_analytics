from django.urls import path
from . import views

app_name = 'market_data'

urlpatterns = [
    # Asset endpoints
    path('assets/', views.AssetListView.as_view(), name='asset_list'),
    path('assets/<str:symbol>/', views.AssetDetailView.as_view(), name='asset_detail'),
    
    # Candlestick chart data for TradingView
    path('candles/<str:symbol>/', views.ChartCandlesView.as_view(), name='chart_candles'),
    
    # Macroeconomic drivers & live sentiment news
    path('macro/', views.MacroIndicatorsView.as_view(), name='macro_indicators'),
    path('news/', views.FinancialNewsView.as_view(), name='financial_news'),
    
    # Sync trigger
    path('sync/', views.SyncMarketDataView.as_view(), name='sync_market_data'),
]

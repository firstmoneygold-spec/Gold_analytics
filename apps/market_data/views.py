from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Asset, HistoricalPrice, MacroIndicator, FinancialNews
from .serializers import AssetSerializer, MacroIndicatorSerializer, FinancialNewsSerializer
from .services.yfinance_service import get_candles_for_chart, sync_asset_historical_data
from .services.macro_service import sync_macro_indicators
from .services.news_service import fetch_live_market_news
from .services.seeder import seed_default_assets


class AssetListView(APIView):
    """
    List all active financial assets with filters for market and asset type.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        market = request.GET.get('market')
        asset_type = request.GET.get('type')
        featured_only = request.GET.get('featured')

        queryset = Asset.objects.filter(is_active=True)
        if market:
            queryset = queryset.filter(market=market.upper())
        if asset_type:
            queryset = queryset.filter(asset_type=asset_type.upper())
        if featured_only:
            queryset = queryset.filter(is_featured=True)

        serializer = AssetSerializer(queryset, many=True)
        return Response(serializer.data)


class AssetDetailView(APIView):
    """
    Get detailed price information and metadata for a specific asset symbol.
    """
    permission_classes = [AllowAny]

    def get(self, request, symbol):
        asset = get_object_or_404(Asset, symbol__iexact=symbol)
        serializer = AssetSerializer(asset)
        return Response(serializer.data)


class ChartCandlesView(APIView):
    """
    Get formatted OHLCV candlestick data for TradingView Lightweight Charts.
    """
    permission_classes = [AllowAny]

    def get(self, request, symbol):
        asset = get_object_or_404(Asset, symbol__iexact=symbol)
        timeframe = request.GET.get('timeframe', HistoricalPrice.Timeframe.DAY_1)
        limit = int(request.GET.get('limit', 300))

        candles = get_candles_for_chart(asset, timeframe=timeframe, limit=limit)
        return Response({
            'symbol': asset.symbol,
            'name': asset.name,
            'currency': asset.currency,
            'display_unit': asset.display_unit,
            'market': asset.market,
            'timeframe': timeframe,
            'count': len(candles),
            'candles': candles
        })


class MacroIndicatorsView(APIView):
    """
    Get current macroeconomic indicators across USA & India.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        market = request.GET.get('market')
        # Seed or refresh if empty
        if MacroIndicator.objects.count() == 0:
            sync_macro_indicators()

        latest_date = MacroIndicator.objects.order_by('-date').values_list('date', flat=True).first()
        queryset = MacroIndicator.objects.filter(date=latest_date) if latest_date else MacroIndicator.objects.all()

        if market:
            queryset = queryset.filter(market=market.upper())

        serializer = MacroIndicatorSerializer(queryset, many=True)
        return Response(serializer.data)


class FinancialNewsView(APIView):
    """
    Get live financial and commodity news with FinBERT sentiment scores.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        market = request.GET.get('market')
        sentiment = request.GET.get('sentiment')
        limit = int(request.GET.get('limit', 20))

        if FinancialNews.objects.count() == 0:
            fetch_live_market_news()

        queryset = FinancialNews.objects.all()
        if market:
            queryset = queryset.filter(market=market.upper())
        if sentiment:
            queryset = queryset.filter(sentiment_label=sentiment.upper())

        serializer = FinancialNewsSerializer(queryset[:limit], many=True)
        return Response(serializer.data)


class SyncMarketDataView(APIView):
    """
    Manual trigger to seed default assets, sync prices, macro, and news.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        created_assets, total_assets = seed_default_assets()
        macro_synced = sync_macro_indicators()
        news_synced = fetch_live_market_news()

        return Response({
            'status': 'success',
            'assets_seeded': f"{created_assets} created / {total_assets} total",
            'macro_synced': len(macro_synced),
            'news_synced': len(news_synced),
            'message': 'Market data successfully initialized and synchronized.'
        })

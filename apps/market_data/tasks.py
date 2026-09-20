import logging
from celery import shared_task
from apps.market_data.models import Asset, HistoricalPrice
from apps.market_data.services.yfinance_service import sync_asset_historical_data
from apps.market_data.services.macro_service import sync_macro_indicators
from apps.market_data.services.news_service import fetch_live_market_news

logger = logging.getLogger(__name__)

@shared_task(name="market_data.sync_all_active_assets")
def sync_all_active_assets_task(timeframe=HistoricalPrice.Timeframe.DAY_1):
    """
    Periodic task to sync OHLCV data for all active assets.
    """
    assets = Asset.objects.filter(is_active=True)
    total_synced = 0
    for asset in assets:
        try:
            count, _ = sync_asset_historical_data(asset, timeframe=timeframe)
            total_synced += count
        except Exception as e:
            logger.error(f"Failed syncing asset {asset.symbol}: {str(e)}")
    return f"Synced {total_synced} bars across {assets.count()} assets."


@shared_task(name="market_data.sync_macro_indicators")
def sync_macro_indicators_task():
    """
    Periodic task to update DXY, USDINR, 10Y Treasury Yields, and VIX.
    """
    indicators = sync_macro_indicators()
    return f"Synced {len(indicators)} macro indicators."


@shared_task(name="market_data.fetch_live_news")
def fetch_live_news_task():
    """
    Periodic task to scrape and sentiment-score financial news.
    """
    news_items = fetch_live_market_news()
    return f"Ingested and analyzed {len(news_items)} news items."

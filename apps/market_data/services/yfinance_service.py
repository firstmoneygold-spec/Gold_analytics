import logging
from decimal import Decimal
import pandas as pd
import yfinance as yf
from django.utils import timezone
from apps.market_data.models import Asset, HistoricalPrice

logger = logging.getLogger(__name__)

# Map internal timeframe codes to yfinance intervals and periods
TIMEFRAME_MAPPING = {
    HistoricalPrice.Timeframe.MIN_15:  {'period': '5d',  'interval': '15m'},
    HistoricalPrice.Timeframe.HOUR_1:  {'period': '1mo', 'interval': '1h'},
    HistoricalPrice.Timeframe.HOUR_4:  {'period': '3mo', 'interval': '1h'},
    HistoricalPrice.Timeframe.DAY_1:   {'period': '5y',  'interval': '1d'},
    HistoricalPrice.Timeframe.WEEK_1:  {'period': '10y', 'interval': '1wk'},
    HistoricalPrice.Timeframe.MONTH_1: {'period': '15y', 'interval': '1mo'},
}

def sync_asset_historical_data(asset: Asset, timeframe: str = HistoricalPrice.Timeframe.DAY_1, force_refresh: bool = False):
    """
    Fetch OHLCV historical time-series data from Yahoo Finance and cache into HistoricalPrice.
    """
    config = TIMEFRAME_MAPPING.get(timeframe, {'period': '5y', 'interval': '1d'})
    symbol = asset.symbol

    logger.info(f"Syncing data for {symbol} ({timeframe}) with period={config['period']}")
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=config['period'], interval=config['interval'])

        if df.empty:
            logger.warning(f"No data returned for symbol {symbol}")
            return 0, None

        # Clean dataframe
        df.reset_index(inplace=True)
        date_col = 'Date' if 'Date' in df.columns else 'Datetime'
        
        # Ensure UTC timezone awareness
        if pd.api.types.is_datetime64tz_dtype(df[date_col]):
            df['timestamp'] = df[date_col].dt.tz_convert('UTC')
        else:
            df['timestamp'] = df[date_col].dt.tz_localize('UTC')

        price_objects = []
        for _, row in df.iterrows():
            ts = row['timestamp']
            open_p = Decimal(str(round(row['Open'], 4)))
            high_p = Decimal(str(round(row['High'], 4)))
            low_p = Decimal(str(round(row['Low'], 4)))
            close_p = Decimal(str(round(row['Close'], 4)))
            vol = int(row['Volume']) if pd.notna(row['Volume']) else 0

            price_objects.append(
                HistoricalPrice(
                    asset=asset,
                    timestamp=ts,
                    timeframe=timeframe,
                    open=open_p,
                    high=high_p,
                    low=low_p,
                    close=close_p,
                    volume=vol
                )
            )

        # Bulk create or update
        HistoricalPrice.objects.bulk_create(
            price_objects,
            update_conflicts=True,
            unique_fields=['asset', 'timestamp', 'timeframe'],
            update_fields=['open', 'high', 'low', 'close', 'volume']
        )

        # Update latest price on asset
        if not df.empty:
            last_row = df.iloc[-1]
            prev_row = df.iloc[-2] if len(df) > 1 else last_row
            latest_close = Decimal(str(round(last_row['Close'], 4)))
            prev_close = Decimal(str(round(prev_row['Close'], 4)))

            change_val = latest_close - prev_close
            change_pct = (change_val / prev_close * 100) if prev_close != 0 else Decimal('0.0')

            asset.last_price = latest_close
            asset.price_change_24h = Decimal(str(round(change_val, 2)))
            asset.price_change_pct_24h = Decimal(str(round(change_pct, 2)))
            asset.save(update_fields=['last_price', 'price_change_24h', 'price_change_pct_24h', 'updated_at'])

        logger.info(f"Successfully synced {len(price_objects)} bars for {symbol}")
        return len(price_objects), df

    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {str(e)}", exc_info=True)
        return 0, None


def get_candles_for_chart(asset: Asset, timeframe: str = HistoricalPrice.Timeframe.DAY_1, limit: int = 300):
    """
    Retrieve candlestick data formatted strictly for TradingView Lightweight Charts (sorted ascending, unique timestamps).
    """
    count = HistoricalPrice.objects.filter(asset=asset, timeframe=timeframe).count()
    if count == 0:
        sync_asset_historical_data(asset, timeframe)

    prices = (
        HistoricalPrice.objects.filter(asset=asset, timeframe=timeframe)
        .order_by('-timestamp')[:limit]
    )
    prices = list(reversed(prices))

    chart_data = []
    seen_timestamps = set()

    for p in prices:
        t = int(p.timestamp.timestamp())
        if t in seen_timestamps:
            continue
        seen_timestamps.add(t)

        chart_data.append({
            'time': t,
            'open': float(p.open),
            'high': float(p.high),
            'low': float(p.low),
            'close': float(p.close),
            'volume': int(p.volume)
        })

    chart_data.sort(key=lambda x: x['time'])
    return chart_data

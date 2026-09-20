import logging
from decimal import Decimal
from django.utils import timezone
import yfinance as yf
from apps.market_data.models import MacroIndicator, Asset

logger = logging.getLogger(__name__)

MACRO_SYMBOLS = {
    # USA / Global Macro Factors
    'DXY': {'symbol': 'DX-Y.NYB', 'name': 'US Dollar Index', 'market': Asset.Market.USA, 'unit': 'pts'},
    'US10Y': {'symbol': '^TNX', 'name': 'US 10-Year Treasury Yield', 'market': Asset.Market.USA, 'unit': '%'},
    'US_VIX': {'symbol': '^VIX', 'name': 'CBOE Volatility Index (VIX)', 'market': Asset.Market.USA, 'unit': 'pts'},
    'CRUDE_WTI': {'symbol': 'CL=F', 'name': 'Crude Oil WTI Futures', 'market': Asset.Market.GLOBAL, 'unit': '$/bbl'},
    
    # India Macro Factors
    'USDINR': {'symbol': 'USDINR=X', 'name': 'USD to INR Exchange Rate', 'market': Asset.Market.INDIA, 'unit': '₹'},
    'INDIA_VIX': {'symbol': '^INDIAVIX', 'name': 'India VIX Volatility Index', 'market': Asset.Market.INDIA, 'unit': 'pts'},
}

def sync_macro_indicators():
    """
    Fetch latest values for critical Gold & Stock macro drivers across US & India.
    """
    today = timezone.now().date()
    synced_indicators = []

    for code, meta in MACRO_SYMBOLS.items():
        try:
            ticker = yf.Ticker(meta['symbol'])
            hist = ticker.history(period='5d', interval='1d')
            
            if hist.empty:
                continue

            last_row = hist.iloc[-1]
            prev_row = hist.iloc[-2] if len(hist) > 1 else last_row

            current_val = Decimal(str(round(last_row['Close'], 4)))
            prev_val = Decimal(str(round(prev_row['Close'], 4)))
            change_pct = (current_val - prev_val) / prev_val * 100 if prev_val != 0 else Decimal('0.0')

            obj, _ = MacroIndicator.objects.update_or_create(
                code=code,
                date=today,
                defaults={
                    'name': meta['name'],
                    'market': meta['market'],
                    'value': current_val,
                    'change_pct': Decimal(str(round(change_pct, 2))),
                    'unit': meta['unit'],
                }
            )
            synced_indicators.append(obj)
            logger.info(f"Macro synced: {code} = {current_val} {meta['unit']} ({change_pct:+.2f}%)")

        except Exception as e:
            logger.error(f"Error syncing macro indicator {code}: {str(e)}")

    return synced_indicators

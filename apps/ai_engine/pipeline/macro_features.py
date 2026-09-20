import numpy as np
from apps.market_data.models import MacroIndicator, Asset

def calculate_macro_score(asset: Asset) -> tuple[float, dict]:
    """
    Calculate macroeconomic sentiment score (-1.0 to +1.0) and drivers breakdown for an asset.
    Database-agnostic (supports SQLite & PostgreSQL).
    """
    latest_indicators = {}
    for m in MacroIndicator.objects.order_by('-date'):
        if m.code not in latest_indicators:
            latest_indicators[m.code] = {
                'value': float(m.value),
                'change_pct': float(m.change_pct)
            }

    score = 0.0
    factors = {}

    dxy = latest_indicators.get('DXY', {'value': 104.0, 'change_pct': 0.0})
    us10y = latest_indicators.get('US10Y', {'value': 4.20, 'change_pct': 0.0})
    us_vix = latest_indicators.get('US_VIX', {'value': 15.0, 'change_pct': 0.0})
    usdinr = latest_indicators.get('USDINR', {'value': 83.5, 'change_pct': 0.0})
    india_vix = latest_indicators.get('INDIA_VIX', {'value': 14.0, 'change_pct': 0.0})
    crude = latest_indicators.get('CRUDE_WTI', {'value': 78.0, 'change_pct': 0.0})

    is_gold_or_silver = asset.asset_type == Asset.AssetType.COMMODITY or 'GOLD' in asset.symbol or 'SILVER' in asset.symbol

    if is_gold_or_silver:
        # 1. DXY Factor (Inverse correlation: -0.85)
        dxy_impact = -1.0 * (dxy['change_pct'] / 1.5)
        dxy_impact = np.clip(dxy_impact, -1.0, 1.0)
        factors['DXY_Impact'] = round(float(dxy_impact), 2)

        # 2. Yield Factor (Inverse correlation)
        yield_impact = -1.0 * (us10y['change_pct'] / 2.0)
        yield_impact = np.clip(yield_impact, -1.0, 1.0)
        factors['US10Y_Impact'] = round(float(yield_impact), 2)

        # 3. Safe-haven VIX spike factor
        vix_impact = (us_vix['change_pct'] / 5.0)
        factors['VIX_SafeHaven_Impact'] = round(float(np.clip(vix_impact, -1.0, 1.0)), 2)

        # 4. For Indian Gold (GOLDBEES, MCX): INR depreciation increases domestic Gold price
        if asset.market == Asset.Market.INDIA:
            inr_depreciation_impact = (usdinr['change_pct'] / 1.0)
            factors['USDINR_Domestic_Boost'] = round(float(np.clip(inr_depreciation_impact, -1.0, 1.0)), 2)
            score = (dxy_impact * 0.35) + (yield_impact * 0.25) + (inr_depreciation_impact * 0.25) + (vix_impact * 0.15)
        else:
            score = (dxy_impact * 0.45) + (yield_impact * 0.35) + (vix_impact * 0.20)

    else:
        # Equities / Indices logic (S&P500, NIFTY50, NVDA, RELIANCE)
        yield_impact = -1.0 * (us10y['change_pct'] / 3.0)
        vix_impact = -1.0 * (us_vix['change_pct'] / 5.0 if asset.market == Asset.Market.USA else india_vix['change_pct'] / 5.0)
        factors['Yield_Impact'] = round(float(np.clip(yield_impact, -1.0, 1.0)), 2)
        factors['Volatility_Impact'] = round(float(np.clip(vix_impact, -1.0, 1.0)), 2)
        
        score = (yield_impact * 0.50) + (vix_impact * 0.50)

    macro_score = float(np.clip(score, -1.0, 1.0))
    return round(macro_score, 2), factors

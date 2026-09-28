import numpy as np
from apps.market_data.models import MacroIndicator, Asset

def calculate_macro_score(asset: Asset) -> tuple[float, dict]:
    """
    Calculate quantitative macroeconomic alpha score (-1.0 to +1.0) and econometric factor breakdown.
    Incorporates:
    - Real Interest Rate Sensitivity (US 10Y Yields)
    - Currency Valuation Elasticity (US Dollar Index DXY)
    - Safe-Haven Volatility Regime (CBOE VIX / India VIX)
    - FX Pass-Through for Domestic Indian Assets (USD/INR)
    - Commodity Inflation Spillover (WTI Crude Oil)
    """
    latest_indicators = {}
    for m in MacroIndicator.objects.order_by('-date'):
        if m.code not in latest_indicators:
            latest_indicators[m.code] = {
                'value': float(m.value),
                'change_pct': float(m.change_pct)
            }

    dxy = latest_indicators.get('DXY', {'value': 104.0, 'change_pct': 0.0})
    us10y = latest_indicators.get('US10Y', {'value': 4.20, 'change_pct': 0.0})
    us_vix = latest_indicators.get('US_VIX', {'value': 15.0, 'change_pct': 0.0})
    usdinr = latest_indicators.get('USDINR', {'value': 83.5, 'change_pct': 0.0})
    india_vix = latest_indicators.get('INDIA_VIX', {'value': 14.0, 'change_pct': 0.0})
    crude = latest_indicators.get('CRUDE_WTI', {'value': 78.0, 'change_pct': 0.0})

    factors = {}
    is_gold_or_silver = (
        asset.asset_type == Asset.AssetType.COMMODITY or 
        'GOLD' in asset.symbol or 
        'SILVER' in asset.symbol or 
        'GC=' in asset.symbol
    )
    is_india = (asset.market == Asset.Market.INDIA) or (asset.currency == 'INR')

    if is_gold_or_silver:
        # 1. DXY Currency Elasticity (Beta ~ -0.80)
        # Gold is globally denominated in USD; DXY rise creates negative pricing pressure.
        dxy_beta = -0.80
        dxy_shift = float(dxy['change_pct'])
        dxy_factor = np.clip(dxy_beta * (dxy_shift / 1.2), -1.0, 1.0)
        factors['DXY_Currency_Elasticity'] = round(float(dxy_factor), 2)

        # 2. Real Yield & Opportunity Cost Transmission (US 10Y Yields)
        # Gold has zero yield; rising bond yields increase holding opportunity cost.
        yield_beta = -0.75
        yield_shift = float(us10y['change_pct'])
        yield_factor = np.clip(yield_beta * (yield_shift / 1.5), -1.0, 1.0)
        factors['Real_Yield_Opportunity_Cost'] = round(float(yield_factor), 2)

        # 3. Safe-Haven & Geopolitical Volatility Premium (VIX Regime)
        vix_val = float(us_vix['value'])
        vix_shift = float(us_vix['change_pct'])
        # High absolute VIX (>20) or sharp spikes produce positive safe-haven demand
        vix_base = max(0.0, (vix_val - 16.0) / 10.0)
        vix_momentum = vix_shift / 8.0
        vix_factor = np.clip((vix_base * 0.4) + (vix_momentum * 0.6), -1.0, 1.0)
        factors['SafeHaven_Risk_Premium'] = round(float(vix_factor), 2)

        # 4. Crude Oil & Energy Inflation Transmission
        crude_shift = float(crude['change_pct'])
        inflation_factor = np.clip(crude_shift / 4.0, -1.0, 1.0)
        factors['Inflation_Hedge_Factor'] = round(float(inflation_factor), 2)

        # 5. Domestic Indian Currency Pass-Through (USD/INR Depreciation Boost)
        if is_india:
            inr_shift = float(usdinr['change_pct'])
            inr_factor = np.clip(inr_shift / 0.8, -1.0, 1.0)
            factors['USDINR_Landed_Cost_Boost'] = round(float(inr_factor), 2)

            score = (
                (dxy_factor * 0.30) +
                (yield_factor * 0.25) +
                (inr_factor * 0.25) +
                (vix_factor * 0.12) +
                (inflation_factor * 0.08)
            )
        else:
            score = (
                (dxy_factor * 0.40) +
                (yield_factor * 0.30) +
                (vix_factor * 0.20) +
                (inflation_factor * 0.10)
            )

    else:
        # Equities / Indices Factor Transmission
        # Yield Pressure (Discount rate on future cash flows)
        yield_shift = float(us10y['change_pct'])
        yield_impact = np.clip(-1.0 * (yield_shift / 2.5), -1.0, 1.0)
        
        # Volatility Sentiment
        vix_series = india_vix if is_india else us_vix
        vix_shift = float(vix_series['change_pct'])
        vol_impact = np.clip(-1.0 * (vix_shift / 6.0), -1.0, 1.0)

        # Energy Input Cost for Industrial Equities
        crude_shift = float(crude['change_pct'])
        energy_cost = np.clip(-1.0 * (crude_shift / 5.0), -1.0, 1.0)

        factors['Discount_Rate_Impact'] = round(float(yield_impact), 2)
        factors['Market_Volatility_Regime'] = round(float(vol_impact), 2)
        factors['Energy_Input_Cost'] = round(float(energy_cost), 2)

        score = (yield_impact * 0.45) + (vol_impact * 0.40) + (energy_cost * 0.15)

    macro_score = float(np.clip(score, -1.0, 1.0))
    return round(macro_score, 2), factors


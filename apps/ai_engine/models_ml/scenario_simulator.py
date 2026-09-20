from decimal import Decimal
from apps.market_data.models import Asset

def simulate_macro_scenario(
    asset: Asset, 
    fed_rate_change_bps: float = 0.0,
    dxy_change_pct: float = 0.0,
    usdinr_change_pct: float = 0.0,
    crude_oil_change_pct: float = 0.0,
    gold_duty_change_pct: float = 0.0
) -> dict:
    """
    Simulate predicted price impact on Gold or Stock given hypothetical macro shocks.
    """
    current_price = float(asset.last_price or 2350.0)
    is_gold = 'GOLD' in asset.symbol or 'GC=F' in asset.symbol or 'GLD' in asset.symbol
    is_india = asset.market == Asset.Market.INDIA

    predicted_change_pct = 0.0
    impact_breakdown = {}

    if is_gold:
        # 1. Fed rate cut impact (50 bps cut ~ +2.2% gold gain)
        rate_impact = -1.0 * (fed_rate_change_bps / 25.0) * 1.10
        predicted_change_pct += rate_impact
        impact_breakdown['Fed Rate Adjustment'] = f"{rate_impact:+.2f}%"

        # 2. DXY impact (-1% DXY ~ +1.3% Gold gain)
        dxy_impact = -1.3 * dxy_change_pct
        predicted_change_pct += dxy_impact
        impact_breakdown['US Dollar Index (DXY) Shift'] = f"{dxy_impact:+.2f}%"

        # 3. Crude oil inflation pass-through (+10% crude ~ +1.2% gold)
        crude_impact = crude_oil_change_pct * 0.12
        predicted_change_pct += crude_impact
        impact_breakdown['Crude Oil Inflation Push'] = f"{crude_impact:+.2f}%"

        # 4. Indian Domestic factors (USDINR & Import Duty)
        if is_india:
            rupee_impact = usdinr_change_pct * 0.95
            duty_impact = gold_duty_change_pct * 1.0
            predicted_change_pct += rupee_impact + duty_impact
            impact_breakdown['USD/INR Depreciation Factor'] = f"{rupee_impact:+.2f}%"
            impact_breakdown['Customs Duty Adjustment'] = f"{duty_impact:+.2f}%"

    else:
        # Stock / Equity scenario
        rate_impact = -1.0 * (fed_rate_change_bps / 25.0) * 1.4
        crude_impact = -1.0 * (crude_oil_change_pct * 0.10)
        predicted_change_pct += rate_impact + crude_impact
        impact_breakdown['Interest Rate Sensitivity'] = f"{rate_impact:+.2f}%"
        impact_breakdown['Crude Energy Cost Impact'] = f"{crude_impact:+.2f}%"

    new_predicted_price = current_price * (1.0 + (predicted_change_pct / 100.0))

    return {
        'asset_symbol': asset.symbol,
        'asset_name': asset.name,
        'currency': asset.currency,
        'display_unit': asset.display_unit,
        'current_price': round(current_price, 2),
        'simulated_price': round(new_predicted_price, 2),
        'net_impact_pct': round(predicted_change_pct, 2),
        'direction': 'BULLISH' if predicted_change_pct > 0 else 'BEARISH' if predicted_change_pct < 0 else 'NEUTRAL',
        'breakdown': impact_breakdown
    }

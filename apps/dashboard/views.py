from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.market_data.models import Asset, MacroIndicator, FinancialNews
from apps.ai_engine.models import PredictionRecord, AccuracyAudit
from apps.ai_engine.models_ml.predictor import generate_ai_prediction
from apps.ai_engine.models_ml.physical_gold_service import get_physical_gold_rates_and_prediction
from apps.market_data.services.seeder import seed_default_assets

def home_view(request):
    """
    Main portal:
    - Renders high-converting SaaS Landing page for unauthenticated visitors.
    - Renders full AI Trading Terminal & TradingView Analytics Dashboard for logged-in users.
    """
    # Query all active assets and categorize (with auto-migration on fresh cloud dyno)
    try:
        all_assets = Asset.objects.filter(is_active=True)
        if not all_assets.exists():
            seed_default_assets()
            all_assets = Asset.objects.filter(is_active=True)
    except Exception:
        from django.core.management import call_command
        call_command('migrate', interactive=False)
        seed_default_assets()
        all_assets = Asset.objects.filter(is_active=True)

    if not request.user.is_authenticated:
        featured_assets = all_assets.filter(is_featured=True)[:8]
        try:
            accuracy_audits = AccuracyAudit.objects.all().order_by('-directional_win_rate')[:4]
        except Exception:
            accuracy_audits = []
        return render(request, 'dashboard/landing.html', {
            'featured_assets': featured_assets,
            'accuracy_audits': accuracy_audits,
        })

    # User is Authenticated — Render Trading Dashboard
    user = request.user

    # Categories
    gold_and_metals = all_assets.filter(asset_type=Asset.AssetType.COMMODITY)
    us_stocks = all_assets.filter(asset_type=Asset.AssetType.EQUITY, market=Asset.Market.USA)
    india_stocks = all_assets.filter(asset_type=Asset.AssetType.EQUITY, market=Asset.Market.INDIA)
    market_indices = all_assets.filter(asset_type=Asset.AssetType.INDEX)

    # Selected asset (from query param or default to market gold)
    symbol_param = request.GET.get('symbol')
    if symbol_param:
        selected_asset = Asset.objects.filter(symbol__iexact=symbol_param).first() or all_assets.first()
    else:
        if user.preferred_market == Asset.Market.INDIA:
            selected_asset = Asset.objects.filter(symbol='GOLDBEES.NS').first() or all_assets.first()
        else:
            selected_asset = Asset.objects.filter(symbol='GC=F').first() or all_assets.first()

    # Latest AI Prediction for this asset
    latest_prediction = (
        PredictionRecord.objects.filter(asset=selected_asset)
        .order_by('-created_at')
        .first()
    )

    if not latest_prediction:
        try:
            latest_prediction = generate_ai_prediction(selected_asset, user=None)
        except Exception:
            latest_prediction = None

    # Physical Gold 24K, 22K, 18K Buy and Sell Predictions
    physical_gold = get_physical_gold_rates_and_prediction(selected_asset)

    # Ticker bar assets
    ticker_assets = all_assets.filter(is_featured=True)

    # Macro Indicators
    latest_macro = MacroIndicator.objects.order_by('-date', 'code')[:8]

    # Live Financial News
    recent_news = FinancialNews.objects.all().order_by('-published_at')[:8]

    # Accuracy audits
    accuracy_audits = AccuracyAudit.objects.all().order_by('-directional_win_rate')[:6]

    can_predict, quota_msg = user.can_make_prediction()

    context = {
        'user': user,
        'selected_asset': selected_asset,
        'all_assets': all_assets,
        'gold_and_metals': gold_and_metals,
        'us_stocks': us_stocks,
        'india_stocks': india_stocks,
        'market_indices': market_indices,
        'ticker_assets': ticker_assets,
        'latest_prediction': latest_prediction,
        'physical_gold': physical_gold,
        'latest_macro': latest_macro,
        'recent_news': recent_news,
        'accuracy_audits': accuracy_audits,
        'can_predict': can_predict,
        'quota_msg': quota_msg,
    }
    return render(request, 'dashboard/index.html', context)

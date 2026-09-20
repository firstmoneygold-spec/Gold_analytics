from datetime import timedelta
from django.utils import timezone
from apps.market_data.models import FinancialNews, Asset

def calculate_sentiment_score(asset: Asset) -> tuple[float, int]:
    """
    Calculate weighted NLP sentiment polarity score (-1.0 to +1.0) over recent 7 days.
    """
    seven_days_ago = timezone.now() - timedelta(days=7)
    
    # Query news specific to this asset or matching its market
    news_qs = FinancialNews.objects.filter(
        published_at__gte=seven_days_ago
    ).filter(
        models_filter_asset(asset)
    ).order_by('-published_at')[:15]

    if not news_qs.exists():
        # Fallback to general market news
        news_qs = FinancialNews.objects.filter(
            published_at__gte=seven_days_ago,
            market=asset.market
        ).order_by('-published_at')[:10]

    if not news_qs.exists():
        return 0.0, 0

    scores = []
    weights = []
    now = timezone.now()

    for idx, item in enumerate(news_qs):
        # Exponential decay weight based on age (in hours)
        age_hours = max((now - item.published_at).total_seconds() / 3600.0, 1.0)
        weight = 1.0 / (1.0 + (age_hours / 24.0))  # higher weight for fresh news
        
        scores.append(item.sentiment_score * weight)
        weights.append(weight)

    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0, 0

    weighted_score = sum(scores) / total_weight
    weighted_score = max(min(weighted_score, 1.0), -1.0)
    return round(float(weighted_score), 2), len(news_qs)


def models_filter_asset(asset: Asset):
    from django.db.models import Q
    return Q(asset=asset) | Q(title__icontains=asset.name.split()[0])

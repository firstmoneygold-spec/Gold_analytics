import logging
import xml.etree.ElementTree as ET
import re
from datetime import datetime
import requests
from django.utils import timezone
from apps.market_data.models import FinancialNews, Asset

logger = logging.getLogger(__name__)

# Financial Sentiment Lexicon for Gold & Equities NLP Scoring
BULLISH_KEYWORDS = {
    'rally', 'surge', 'jump', 'gain', 'high', 'record', 'bullish', 'breakout', 
    'buy', 'strong', 'outperform', 'profit', 'expansion', 'rate cut', 'easing',
    'growth', 'stimulus', 'dividend', 'all-time high', 'upside', 'inflows', 'soars'
}

BEARISH_KEYWORDS = {
    'plunge', 'drop', 'slump', 'tumble', 'fall', 'loss', 'bearish', 'breakdown', 
    'sell', 'weak', 'underperform', 'recession', 'inflation', 'rate hike', 'tightening',
    'downside', 'outflows', 'debt', 'crash', 'deficit', 'sanction', 'warning', 'sinks'
}

NEWS_FEEDS = [
    {
        'url': 'https://news.google.com/rss/search?q=gold+price+OR+gold+market&hl=en-US&gl=US&ceid=US:en',
        'market': Asset.Market.USA,
        'category': 'Gold & Commodities USA'
    },
    {
        'url': 'https://news.google.com/rss/search?q=gold+price+india+OR+MCX+gold&hl=en-IN&gl=IN&ceid=IN:en',
        'market': Asset.Market.INDIA,
        'category': 'Gold India MCX'
    },
    {
        'url': 'https://news.google.com/rss/search?q=stock+market+india+NSE+NIFTY&hl=en-IN&gl=IN&ceid=IN:en',
        'market': Asset.Market.INDIA,
        'category': 'Indian Equities'
    },
    {
        'url': 'https://news.google.com/rss/search?q=us+stock+market+sp500+fed&hl=en-US&gl=US&ceid=US:en',
        'market': Asset.Market.USA,
        'category': 'US Equities & Macro'
    }
]

def analyze_sentiment(text: str) -> tuple[float, str, float]:
    """
    Calculate NLP sentiment polarity score (-1.0 to +1.0) and confidence.
    """
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    
    bull_count = sum(1 for w in words if w in BULLISH_KEYWORDS)
    bear_count = sum(1 for w in words if w in BEARISH_KEYWORDS)
    
    # Check multi-word keywords
    for kw in ['all-time high', 'rate cut', 'rate hike']:
        if kw in text_lower:
            if kw in BULLISH_KEYWORDS:
                bull_count += 2
            else:
                bear_count += 2

    total = bull_count + bear_count
    if total == 0:
        return 0.0, FinancialNews.SentimentLabel.NEUTRAL, 0.50

    score = (bull_count - bear_count) / total
    score = max(min(score, 1.0), -1.0)

    confidence = round(min(0.5 + (total * 0.1), 0.95), 2)

    if score >= 0.20:
        label = FinancialNews.SentimentLabel.BULLISH
    elif score <= -0.20:
        label = FinancialNews.SentimentLabel.BEARISH
    else:
        label = FinancialNews.SentimentLabel.NEUTRAL

    return round(score, 2), label, confidence


def fetch_live_market_news(limit_per_feed: int = 10):
    """
    Scrape, analyze sentiment, and store live financial news feeds for US & India.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) TrendMasterAI/1.0'}
    created_news = []

    for feed_info in NEWS_FEEDS:
        try:
            resp = requests.get(feed_info['url'], headers=headers, timeout=10)
            if resp.status_code != 200:
                continue

            root = ET.fromstring(resp.content)
            items = root.findall('.//item')[:limit_per_feed]

            for item in items:
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                pub_date_str = item.find('pubDate').text if item.find('pubDate') is not None else ''
                source_tag = item.find('source')
                source_name = source_tag.text if source_tag is not None else 'Financial News'

                if not title or not link:
                    continue

                # Parse publication date
                try:
                    pub_dt = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %Z')
                    pub_dt = timezone.make_aware(pub_dt, timezone.utc)
                except Exception:
                    pub_dt = timezone.now()

                # Clean Title & extract clean source
                clean_title = title.split(' - ')[0] if ' - ' in title else title
                sentiment_score, sentiment_label, confidence = analyze_sentiment(clean_title)

                # Match with asset if applicable
                matched_asset = None
                if 'gold' in clean_title.lower():
                    matched_asset = Asset.objects.filter(symbol__in=['GC=F', 'GOLDBEES.NS']).first()
                elif 'nifty' in clean_title.lower():
                    matched_asset = Asset.objects.filter(symbol='^NSEI').first()
                elif 's&p' in clean_title.lower() or 'fed' in clean_title.lower():
                    matched_asset = Asset.objects.filter(symbol='SPY').first()

                obj, created = FinancialNews.objects.update_or_create(
                    url=link,
                    defaults={
                        'title': clean_title,
                        'source': source_name,
                        'market': feed_info['market'],
                        'asset': matched_asset,
                        'published_at': pub_dt,
                        'sentiment_score': sentiment_score,
                        'sentiment_label': sentiment_label,
                        'sentiment_confidence': confidence,
                    }
                )
                if created:
                    created_news.append(obj)

        except Exception as e:
            logger.error(f"Error fetching news feed {feed_info['category']}: {str(e)}")

    logger.info(f"Ingested and analyzed {len(created_news)} new financial news items.")
    return created_news

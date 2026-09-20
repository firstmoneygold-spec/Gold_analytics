from apps.market_data.models import Asset

DEFAULT_ASSETS = [
    # =========================================================================
    # 🪙 Precious Metals & Commodities (Gold & Silver - USA & India)
    # =========================================================================
    {
        'symbol': 'GC=F',
        'name': 'Gold COMEX Futures (Global Spot $/oz)',
        'asset_type': Asset.AssetType.COMMODITY,
        'market': Asset.Market.USA,
        'currency': Asset.Currency.USD,
        'display_unit': 'oz',
        'is_featured': True,
        'description': 'Global benchmark COMEX continuous Gold Futures in USD per Troy Ounce.'
    },
    {
        'symbol': 'GOLDBEES.NS',
        'name': 'Nippon India ETF Gold BeES (₹/1g)',
        'asset_type': Asset.AssetType.COMMODITY,
        'market': Asset.Market.INDIA,
        'currency': Asset.Currency.INR,
        'display_unit': '1g',
        'is_featured': True,
        'description': 'Leading physical Gold ETF in India tracking domestic gold prices on NSE.'
    },
    {
        'symbol': 'GLD',
        'name': 'SPDR Gold Shares ETF',
        'asset_type': Asset.AssetType.COMMODITY,
        'market': Asset.Market.USA,
        'currency': Asset.Currency.USD,
        'display_unit': 'share',
        'is_featured': False,
        'description': 'Largest physically backed Gold ETF in the world (NYSE Arca).'
    },
    {
        'symbol': 'SI=F',
        'name': 'Silver COMEX Futures ($/oz)',
        'asset_type': Asset.AssetType.COMMODITY,
        'market': Asset.Market.USA,
        'currency': Asset.Currency.USD,
        'display_unit': 'oz',
        'is_featured': False,
        'description': 'Continuous COMEX Silver Futures in USD per Troy Ounce.'
    },
    {
        'symbol': 'SILVERBEES.NS',
        'name': 'Nippon India ETF Silver BeES (₹/1g)',
        'asset_type': Asset.AssetType.COMMODITY,
        'market': Asset.Market.INDIA,
        'currency': Asset.Currency.INR,
        'display_unit': '1g',
        'is_featured': False,
        'description': 'Leading physical Silver ETF in India on NSE.'
    },

    # =========================================================================
    # 🇺🇸 United States Mega-Cap Stocks
    # =========================================================================
    {
        'symbol': 'NVDA',
        'name': 'NVIDIA Corporation',
        'asset_type': Asset.AssetType.EQUITY,
        'market': Asset.Market.USA,
        'currency': Asset.Currency.USD,
        'display_unit': 'share',
        'is_featured': True,
        'description': 'Global leader in GPU accelerated computing, AI chips, and data centers.'
    },
    {
        'symbol': 'AAPL',
        'name': 'Apple Inc.',
        'asset_type': Asset.AssetType.EQUITY,
        'market': Asset.Market.USA,
        'currency': Asset.Currency.USD,
        'display_unit': 'share',
        'is_featured': True,
        'description': 'World largest consumer technology, iPhone, Mac, and services ecosystem.'
    },
    {
        'symbol': 'TSLA',
        'name': 'Tesla, Inc.',
        'asset_type': Asset.AssetType.EQUITY,
        'market': Asset.Market.USA,
        'currency': Asset.Currency.USD,
        'display_unit': 'share',
        'is_featured': False,
        'description': 'Electric vehicle pioneer, autonomous driving AI, and energy storage.'
    },
    {
        'symbol': 'MSFT',
        'name': 'Microsoft Corporation',
        'asset_type': Asset.AssetType.EQUITY,
        'market': Asset.Market.USA,
        'currency': Asset.Currency.USD,
        'display_unit': 'share',
        'is_featured': False,
        'description': 'Enterprise software, Azure cloud computing infrastructure, and OpenAI partner.'
    },
    {
        'symbol': 'AMZN',
        'name': 'Amazon.com, Inc.',
        'asset_type': Asset.AssetType.EQUITY,
        'market': Asset.Market.USA,
        'currency': Asset.Currency.USD,
        'display_unit': 'share',
        'is_featured': False,
        'description': 'Global e-commerce marketplace and AWS cloud infrastructure leader.'
    },
    {
        'symbol': 'GOOGL',
        'name': 'Alphabet Inc. (Google)',
        'asset_type': Asset.AssetType.EQUITY,
        'market': Asset.Market.USA,
        'currency': Asset.Currency.USD,
        'display_unit': 'share',
        'is_featured': False,
        'description': 'Search engine giant, YouTube, Google Cloud, and Gemini AI.'
    },

    # =========================================================================
    # 🇮🇳 Indian Bluechip Equities (NSE / BSE)
    # =========================================================================
    {
        'symbol': 'RELIANCE.NS',
        'name': 'Reliance Industries Ltd.',
        'asset_type': Asset.AssetType.EQUITY,
        'market': Asset.Market.INDIA,
        'currency': Asset.Currency.INR,
        'display_unit': 'share',
        'is_featured': True,
        'description': 'India largest corporate conglomerate across Oil-to-Chemicals, Retail, and Jio Telecom.'
    },
    {
        'symbol': 'TCS.NS',
        'name': 'Tata Consultancy Services Ltd.',
        'asset_type': Asset.AssetType.EQUITY,
        'market': Asset.Market.INDIA,
        'currency': Asset.Currency.INR,
        'display_unit': 'share',
        'is_featured': False,
        'description': 'India premier global IT consulting, AI solutions, and digital services powerhouse.'
    },
    {
        'symbol': 'HDFCBANK.NS',
        'name': 'HDFC Bank Ltd.',
        'asset_type': Asset.AssetType.EQUITY,
        'market': Asset.Market.INDIA,
        'currency': Asset.Currency.INR,
        'display_unit': 'share',
        'is_featured': False,
        'description': 'Largest private sector financial powerhouse and mortgage leader in India.'
    },
    {
        'symbol': 'INFY.NS',
        'name': 'Infosys Limited',
        'asset_type': Asset.AssetType.EQUITY,
        'market': Asset.Market.INDIA,
        'currency': Asset.Currency.INR,
        'display_unit': 'share',
        'is_featured': False,
        'description': 'Multinational digital services and enterprise consulting company.'
    },
    {
        'symbol': 'TATASTEEL.NS',
        'name': 'Tata Steel Ltd.',
        'asset_type': Asset.AssetType.EQUITY,
        'market': Asset.Market.INDIA,
        'currency': Asset.Currency.INR,
        'display_unit': 'share',
        'is_featured': False,
        'description': 'Major global steel producing and industrial infrastructure corporation.'
    },
    {
        'symbol': 'ICICIBANK.NS',
        'name': 'ICICI Bank Ltd.',
        'asset_type': Asset.AssetType.EQUITY,
        'market': Asset.Market.INDIA,
        'currency': Asset.Currency.INR,
        'display_unit': 'share',
        'is_featured': False,
        'description': 'Leading multinational Indian private banking and wealth management institution.'
    },
    {
        'symbol': 'ITC.NS',
        'name': 'ITC Limited',
        'asset_type': Asset.AssetType.EQUITY,
        'market': Asset.Market.INDIA,
        'currency': Asset.Currency.INR,
        'display_unit': 'share',
        'is_featured': False,
        'description': 'Major Indian FMCG, hotels, paperboards, and agribusiness conglomerate.'
    },

    # =========================================================================
    # 📈 Major Benchmark Market Indices
    # =========================================================================
    {
        'symbol': '^NSEI',
        'name': 'NIFTY 50 Index',
        'asset_type': Asset.AssetType.INDEX,
        'market': Asset.Market.INDIA,
        'currency': Asset.Currency.INR,
        'display_unit': 'points',
        'is_featured': True,
        'description': 'National Stock Exchange benchmark index tracking top 50 Indian companies.'
    },
    {
        'symbol': '^NSEBANK',
        'name': 'BANK NIFTY Index',
        'asset_type': Asset.AssetType.INDEX,
        'market': Asset.Market.INDIA,
        'currency': Asset.Currency.INR,
        'display_unit': 'points',
        'is_featured': False,
        'description': 'Index tracking the 12 most liquid Indian banking financial institutions.'
    },
    {
        'symbol': '^BSESN',
        'name': 'BSE SENSEX Index',
        'asset_type': Asset.AssetType.INDEX,
        'market': Asset.Market.INDIA,
        'currency': Asset.Currency.INR,
        'display_unit': 'points',
        'is_featured': False,
        'description': 'Oldest stock market benchmark index of 30 well-established companies on BSE.'
    },
    {
        'symbol': 'SPY',
        'name': 'S&P 500 ETF (SPY)',
        'asset_type': Asset.AssetType.INDEX,
        'market': Asset.Market.USA,
        'currency': Asset.Currency.USD,
        'display_unit': 'points',
        'is_featured': True,
        'description': 'Benchmark index representing 500 largest US publicly traded corporations.'
    },
    {
        'symbol': 'QQQ',
        'name': 'Nasdaq 100 ETF (QQQ)',
        'asset_type': Asset.AssetType.INDEX,
        'market': Asset.Market.USA,
        'currency': Asset.Currency.USD,
        'display_unit': 'points',
        'is_featured': False,
        'description': 'Index ETF tracking the 100 largest non-financial innovative US tech leaders.'
    }
]

def seed_default_assets():
    """Seed or update the default asset universe."""
    created_count = 0
    for asset_dict in DEFAULT_ASSETS:
        obj, created = Asset.objects.update_or_create(
            symbol=asset_dict['symbol'],
            defaults=asset_dict
        )
        if created:
            created_count += 1
    return created_count, len(DEFAULT_ASSETS)

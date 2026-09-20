# TrendMaster AI — Dual-Market (USA 🇺🇸 & India 🇮🇳) Gold & Stock Prediction SaaS
## Complete Master Architecture & Implementation Specification

---

## 1. Project Overview & Objectives
**TrendMaster AI** is an advanced, production-ready SaaS web application (inspired by platforms like TrueTrendView and TradingView) designed for high-accuracy price forecasting, directional trend analysis, and real-time sentiment intelligence catering specifically to both **Indian (NSE/BSE/MCX)** and **United States (NYSE/NASDAQ/COMEX)** financial markets.

### Core Value Propositions
1. **Dual-Market Specialization (USA 🇺🇸 & India 🇮🇳)**:
   - Dedicated support for US Equities, Commodities, and Macro drivers alongside Indian Equities, MCX Commodities, and RBI/Domestic drivers.
   - Instant toggle between **USD ($) / Troy Ounce (oz)** and **INR (₹) / 10 Grams (10g)** for Gold/Silver.
   - Dual market session timers (EST/EDT for US & IST for India NSE/BSE/MCX).
2. **Strict User Access & SaaS Monetization**:
   - Full auth-gated access (Free vs. Pro Trader vs. Institutional tiers) with credit quotas.
   - Multi-currency billing support: **Stripe (USD/Global)** & **Razorpay / UPI (INR/India)**.
3. **Dual-Engine Prediction Pipeline**:
   - **Quantitative Time-Series**: 5–10 years of historical OHLCV data + multi-indicator technical analysis + localized macro factors (DXY, USD/INR, Fed Rate, RBI Repo Rate, US10Y, India 10Y G-Sec).
   - **Real-Time News NLP Engine**: FinBERT / LLM-based sentiment scoring from global (Reuters/Bloomberg/Yahoo Finance) and Indian (Economic Times/Moneycontrol/LiveMint) streams.
4. **High-Accuracy Trend Prediction**: Volatility-adjusted directional forecasting (targeting >85–90% directional hit rate with high-confidence trade setups, entry/exit levels, and risk-to-reward metrics).
5. **Interactive TradingView-Grade UI**: Candlestick charts with dynamic prediction corridors, support/resistance bands, and live market sentiment heatmaps.

---

## 2. Technical Stack & Infrastructure

| Component | Technology | Description / Usage |
| :--- | :--- | :--- |
| **Backend Framework** | **Django 5.x & Django REST Framework (DRF)** | Robust Python web framework with modular apps and RESTful API endpoints |
| **Database** | **PostgreSQL (with TimescaleDB optional)** | Relational storage for users, subscriptions, time-series OHLCV data, and news items |
| **Async Tasks & Cache** | **Redis & Celery** | Background data scraping, ML model inference, scheduled price updates, and alerts |
| **Frontend & UI** | **HTML5, Modern CSS, Alpine.js / HTMX** | Dark-mode Obsidian/Gold theme, micro-interactions, responsive mobile/desktop UX |
| **Charting Engine** | **TradingView Lightweight Charts** | Fast, interactive candlestick charts with custom AI prediction overlays |
| **AI / ML Stack** | **LightGBM / XGBoost, PyTorch (LSTM), FinBERT, Scikit-learn** | Hybrid quantitative + sentiment prediction models |
| **Market Data APIs** | **`yfinance`, FRED API, NewsAPI, GNews, FMP** | Dual-market historical prices, macro indicators, and live market news feeds |
| **SaaS Billing & Auth** | **Stripe (USD) + Razorpay (INR) + `django-allauth` / JWT** | Global and domestic payment gateways, secure authentication, and tier gating |

---

## 3. Dual-Market Asset Universe & Macro Factors

### A. United States Market (🇺🇸 USA)
- **Precious Metals & Commodities**:
  - Gold Spot (XAU/USD), COMEX Gold Futures (`GC=F`), SPDR Gold Trust (`GLD`), COMEX Silver (`SI=F`).
- **Indices & Top Equities**:
  - S&P 500 (`SPY`), Nasdaq 100 (`QQQ`), Dow Jones (`DIA`).
  - Mega-Cap Tech: NVIDIA (`NVDA`), Apple (`AAPL`), Tesla (`TSLA`), Microsoft (`MSFT`), Amazon (`AMZN`), Alphabet (`GOOGL`).
- **US Macroeconomic Drivers**:
  - US Dollar Index (`DXY`), US 10-Year Treasury Yield (`^TNX`), US Fed Funds Rate, US CPI/Inflation, CBOE Volatility Index (`^VIX`), Crude Oil WTI (`CL=F`).
- **News Feeds**: Reuters, Bloomberg, Yahoo Finance, CNBC, MarketWatch.

---

### B. Indian Market (🇮🇳 India)
- **Precious Metals & Commodities**:
  - MCX Gold Futures (`GOLD.MCX` / `GOLDBEES.NS`), MCX Silver Futures (`SILVER.MCX` / `SILVERBEES.NS`), Sovereign Gold Bonds (SGB pricing model).
  - Domestic metrics: 24K & 22K Gold rates per 10 grams in INR.
- **Indices & Top Equities**:
  - Nifty 50 (`^NSEI`), Bank Nifty (`^NSEBANK`), BSE Sensex (`^BSESN`), Nifty IT (`^CNXIT`).
  - Top Indian Stocks: Reliance Industries (`RELIANCE.NS`), HDFC Bank (`HDFCBANK.NS`), TCS (`TCS.NS`), Infosys (`INFY.NS`), Tata Steel (`TATASTEEL.NS`), ICICI Bank (`ICICIBANK.NS`).
- **India Macroeconomic Drivers**:
  - USD/INR Exchange Rate (`USDINR=X`), RBI Repo Rate, India CPI Inflation, India 10-Year Government Bond Yield, India VIX (`^INDIAVIX`), Gold Import Duty/Customs tariff adjustments.
- **News Feeds**: The Economic Times, Moneycontrol, LiveMint, Business Standard, NSE/BSE Corporate Announcements.

---

## 4. System Architecture & Core Directory Structure

```
Gold_analytics/
│
├── config/                     # Django Project Configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── wsgi.py
│   ├── urls.py
│   └── settings/
│       ├── __init__.py
│       ├── base.py
│       ├── local.py
│       └── production.py
│
├── apps/
│   ├── users/                  # Custom Auth, Profile, SaaS Tiers, Quotas, Market Preferences
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   │
│   ├── market_data/            # Ingestion for USA & India markets, Macro Indices, Historical Cache
│   │   ├── models.py           # Asset, HistoricalPrice, MacroIndicator, MarketNews
│   │   ├── services/           # yfinance (US & NSE/MCX), FRED, RBI/India macro, News scrapers
│   │   ├── tasks.py            # Celery sync jobs (Market hours aware: EST & IST)
│   │   └── views.py
│   │
│   ├── ai_engine/              # ML Models, FinBERT Sentiment, Signal Generator, Accuracy Auditor
│   │   ├── models.py           # Saved predictions & backtest audits
│   │   ├── pipeline/           # Feature engineering & FinBERT pipeline
│   │   ├── models_ml/          # Trained weights / ensemble logic
│   │   └── views.py
│   │
│   ├── billing/                # Stripe (USD) & Razorpay (INR) Subscriptions & Credits
│   │   ├── models.py
│   │   ├── webhooks.py         # Stripe & Razorpay Webhook handlers
│   │   └── views.py
│   │
│   └── dashboard/              # UI Views, Template renderers, Chart APIs, Market Toggles
│       ├── views.py
│       └── urls.py
│
├── static/                     # CSS, JS (Lightweight charts integration), Images
├── templates/                  # Modern Dark-Themed UI Templates (Dual Market Switcher)
├── requirements.txt            # Python Dependencies
├── docker-compose.yml          # Containerized Postgres, Redis, Django, Celery
└── manage.py
```

---

## 5. Detailed Feature Specifications

### Module A: Authentication, Regional Preferences & SaaS Gating
- **No guest access**: Dashboards, charts, AI predictions, and trade signals require sign-in.
- **Custom User Model**:
  - `email`, `full_name`, `preferred_market` (`USA` / `INDIA` / `ALL`), `preferred_currency` (`USD` / `INR`), `subscription_tier` (`FREE`, `PRO`, `ENTERPRISE`), `credits_remaining`, `is_verified`.
- **SaaS Pricing & Dual Gateways**:
  - **Free Tier**: 3 daily predictions, standard 1-day timeframe, basic news feed.
  - **Pro Trader Tier**: 
    - USA: `$29 / month` via Stripe
    - India: `₹1,999 / month` via Razorpay / UPI
    - Features: Unlimited predictions, multi-timeframe (1H, 4H, 1D, 1W), AI sentiment breakdown, Telegram/WhatsApp/Email trade alerts.
  - **Enterprise Tier**: Dedicated API access, bulk export, automated webhook triggers.

---

### Module B: Dual-Engine Data Pipeline & Market Session Timers
1. **Market Session Timers & Live Clocks**:
   - **USA Market**: NYSE/NASDAQ (9:30 AM - 4:00 PM EST / EDT).
   - **India Equity**: NSE/BSE (9:15 AM - 3:30 PM IST).
   - **India Commodity**: MCX (9:00 AM - 11:30 PM / 11:55 PM IST).
   - **Global Gold Spot**: 24/5 Trading session.
2. **Automated Celery Sync Tasks**:
   - Scheduled tasks that trigger dynamically based on respective market open/close times in EST and IST.
3. **Real-time News Sentiment Analysis**:
   - NLP Engine (FinBERT) processes English headlines from both US global feeds and Indian financial dailies.
   - Outputs sentiment polarity score (`-1.0` Bearish to `+1.0` Bullish) and asset-specific impact tags.

---

### Module C: Prediction & Machine Learning Engine
1. **Hybrid Ensemble Strategy**:
   - **Feature Layer**:
     - Technicals: EMA (9, 21, 50, 200), RSI (14), MACD, Bollinger Bands, ATR, SuperTrend, Pivot Points, Order Block liquidity zones.
     - US Macro Factors: DXY, US10Y, Fed rate delta.
     - India Macro Factors: USD/INR delta, India 10Y Yield, RBI rate delta, India VIX.
     - Sentiment Factor: FinBERT sentiment scores weighted by news recency.
   - **Model Layer**:
     - LightGBM / XGBoost for high-accuracy directional trend classification (Bullish / Bearish / Sideways).
     - Sequence momentum network (LSTM / Temporal Fusion) for price corridor projection.
2. **Actionable Output Schema**:
   - **Trend Signal**: Strong Buy / Buy / Neutral / Sell / Strong Sell with percentage confidence (e.g. 91.8% confidence).
   - **Target Price Range**: Upper Band, Expected Target, Lower Band in chosen currency (`$` or `₹`).
   - **Trade Setup**: Recommended Entry, Stop-Loss (ATR-based), Take-Profit (TP1, TP2), Risk-to-Reward ratio.
3. **Backtesting & Accuracy Audit**:
   - Verifiable accuracy tracker displaying historical win rates across both US and Indian assets.

---

### Module D: Frontend UI & Interactive Analytics
1. **Market Switcher & Currency Toggle**:
   - Top navigation switch: Toggle between **US Market (USD $)** and **India Market (INR ₹)** with seamless asset re-indexing.
   - Gold Unit Toggle: Switch between **$/oz (Global)** and **₹/10g (Domestic India)**.
2. **TradingView Lightweight Charts**:
   - Candlestick visualizer with customizable timeframes, zoom/pan, and dynamic AI overlay zones.
3. **Market Sentiment Heatmap & Live News Digest**:
   - Visual sentiment gauges for both Wall Street and Dalal Street.
4. **Macro "What-If" Scenario Simulator**:
   - US Scenarios: *"What if Fed cuts rate by 50 bps?"*, *"What if DXY drops 2%?"*.
   - India Scenarios: *"What if USD/INR hits 85?"*, *"What if India Import Duty on Gold changes?"*.
5. **Instant Alert System**:
   - Telegram, WhatsApp (India), and Email alert notifications on high-probability breakout signals.

---

## 6. Phased Implementation Roadmap

1. **Phase 1: Environment Setup & Project Scaffolding**
   - Django 5.x project initialization, directory structure, decoupled settings (`base.py`, `local.py`, `production.py`), and `requirements.txt`.
2. **Phase 2: Custom User Authentication & SaaS Profiles**
   - Custom User model with regional preferences (`USA`/`INDIA`, `USD`/`INR`), tier permissions, and auth views (Signup, Login, Password Reset, JWT).
3. **Phase 3: Dual-Market Ingestion & Macro Pipeline (`market_data`)**
   - Models for US & Indian assets, historical OHLCV fetcher (`yfinance`), macro indicator synchronizers (FRED + RBI/USDINR), and news sentiment scrapers.
4. **Phase 4: ML Prediction Engine & FinBERT Sentiment (`ai_engine`)**
   - Feature engineering pipeline (technicals + macros + sentiment), ensemble inference models, trade signal generator, and accuracy audit ledger.
5. **Phase 5: Multi-Currency SaaS Billing (`billing`)**
   - Stripe (USD) & Razorpay (INR) checkout sessions, customer webhooks, and subscription quota managers.
6. **Phase 6: Modern UI & TradingView Charts (`dashboard`)**
   - Obsidian/Gold dark-mode theme, market switcher (US / India), TradingView Lightweight Charts with prediction overlays, and "What-If" simulator.
7. **Phase 7: Celery Async Jobs, Notifications (Telegram/Email), & Docker Deployment**
   - Automated market-hour Celery workers, alert dispatchers, comprehensive test suite, and Docker compose deployment.

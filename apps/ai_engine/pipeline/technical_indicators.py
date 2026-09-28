import numpy as np
import pandas as pd

def calculate_technical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate comprehensive institutional-grade technical indicators on OHLCV dataframe.
    Input df requires: 'open', 'high', 'low', 'close', 'volume'
    Returns enriched DataFrame with momentum, volatility, trend confluence, and pivot features.
    """
    df = df.copy()
    close = df['close'].astype(float)
    high = df['high'].astype(float)
    low = df['low'].astype(float)
    open_p = df['open'].astype(float)
    volume = df['volume'].astype(float)

    # 1. Exponential Moving Average Ribbon (9, 21, 50, 200)
    df['ema_9'] = close.ewm(span=9, adjust=False).mean()
    df['ema_21'] = close.ewm(span=21, adjust=False).mean()
    df['ema_50'] = close.ewm(span=50, adjust=False).mean()
    df['ema_200'] = close.ewm(span=min(len(df), 200), adjust=False).mean()

    # EMA Ribbon Confluence: +1.0 full bullish stack (9>21>50>200), -1.0 full bearish stack
    ema_bullish_stack = (
        (df['ema_9'] > df['ema_21']).astype(int) +
        (df['ema_21'] > df['ema_50']).astype(int) +
        (df['ema_50'] > df['ema_200']).astype(int) +
        (close > df['ema_9']).astype(int)
    )
    df['ema_confluence'] = (ema_bullish_stack - 2.0) / 2.0  # Normalized between -1.0 and +1.0

    # 2. Relative Strength Index (RSI 14) with Momentum Curve
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(window=14, min_periods=1).mean()
    loss = (-delta.clip(upper=0)).rolling(window=14, min_periods=1).mean()
    rs = gain / (loss + 1e-9)
    df['rsi_14'] = 100.0 - (100.0 / (1.0 + rs))

    # RSI Normalized Momentum: Center around 50, with non-linear saturation
    rsi_centered = (df['rsi_14'] - 50.0) / 25.0
    df['rsi_score'] = np.clip(rsi_centered, -1.0, 1.0)

    # 3. MACD (12, 26, 9) with Velocity/Acceleration
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    df['macd_line'] = ema_12 - ema_26
    df['macd_signal'] = df['macd_line'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd_line'] - df['macd_signal']
    df['macd_hist_slope'] = df['macd_hist'].diff().fillna(0.0)

    # 4. Average True Range (ATR 14) & Normalized Volatility Ratio
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df['atr_14'] = tr.rolling(window=14, min_periods=1).mean()
    df['atr_pct'] = (df['atr_14'] / (close + 1e-9)) * 100.0

    # Parkinson Volatility (Extreme Value Estimator - Annualized)
    # sigma_p = sqrt(1 / (4 * ln(2)) * (ln(High/Low))^2) * sqrt(252)
    hl_ratio_sq = (np.log(np.maximum(high / np.maximum(low, 1e-9), 1.0))) ** 2
    parkinson_daily = np.sqrt(hl_ratio_sq / (4.0 * np.log(2.0)))
    df['volatility_annualized'] = parkinson_daily.rolling(window=20, min_periods=1).mean() * np.sqrt(252) * 100.0
    df['volatility_daily'] = df['volatility_annualized'] / np.sqrt(252)

    # 5. Bollinger Bands (20, 2.0) & Volatility Squeeze
    sma_20 = close.rolling(window=20, min_periods=1).mean()
    std_20 = close.rolling(window=20, min_periods=1).std().fillna(0.0)
    df['bb_upper'] = sma_20 + (std_20 * 2.0)
    df['bb_middle'] = sma_20
    df['bb_lower'] = sma_20 - (std_20 * 2.0)
    df['bb_bandwidth'] = (df['bb_upper'] - df['bb_lower']) / (sma_20 + 1e-9)
    df['bb_percent_b'] = (close - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'] + 1e-9)

    # 6. SuperTrend Indicator (10, 3.0)
    multiplier = 3.0
    atr_10 = tr.rolling(window=10, min_periods=1).mean()
    hl2 = (high + low) / 2.0
    upper_band = hl2 + (multiplier * atr_10)
    lower_band = hl2 - (multiplier * atr_10)

    supertrend = pd.Series(index=df.index, dtype=float)
    st_direction = pd.Series(index=df.index, dtype=int)
    in_uptrend = True

    for i in range(len(df)):
        if i == 0:
            supertrend.iloc[i] = lower_band.iloc[i]
            st_direction.iloc[i] = 1
            continue

        curr_close = close.iloc[i]
        prev_close = close.iloc[i - 1]

        if curr_close > upper_band.iloc[i - 1]:
            in_uptrend = True
        elif curr_close < lower_band.iloc[i - 1]:
            in_uptrend = False

        supertrend.iloc[i] = lower_band.iloc[i] if in_uptrend else upper_band.iloc[i]
        st_direction.iloc[i] = 1 if in_uptrend else -1

    df['supertrend'] = supertrend
    df['supertrend_direction'] = st_direction

    # 7. Fast Stochastic Oscillator (14, 3)
    low_14 = low.rolling(window=14, min_periods=1).min()
    high_14 = high.rolling(window=14, min_periods=1).max()
    stoch_k = 100.0 * ((close - low_14) / (high_14 - low_14 + 1e-9))
    df['stoch_k'] = stoch_k.rolling(window=3, min_periods=1).mean()
    df['stoch_score'] = ((df['stoch_k'] - 50.0) / 25.0).clip(-1.0, 1.0)

    # 8. Support / Resistance Pivots (Classic Daily & Fibonacci 30D Retracement)
    recent_high = high.rolling(window=min(len(df), 30), min_periods=1).max()
    recent_low = low.rolling(window=min(len(df), 30), min_periods=1).min()
    range_30d = recent_high - recent_low

    df['fib_618_resistance'] = recent_low + (range_30d * 0.618)
    df['fib_500_midpoint'] = recent_low + (range_30d * 0.500)
    df['fib_382_support'] = recent_low + (range_30d * 0.382)
    df['fib_236_support'] = recent_low + (range_30d * 0.236)

    # Classic Floor Trader Pivots
    prev_h = high.shift(1).fillna(high)
    prev_l = low.shift(1).fillna(low)
    prev_c = close.shift(1).fillna(close)
    df['pivot_p'] = (prev_h + prev_l + prev_c) / 3.0
    df['pivot_r1'] = (2.0 * df['pivot_p']) - prev_l
    df['pivot_s1'] = (2.0 * df['pivot_p']) - prev_h
    df['pivot_r2'] = df['pivot_p'] + (prev_h - prev_l)
    df['pivot_s2'] = df['pivot_p'] - (prev_h - prev_l)

    # 9. Confluence Agreement & Composite Quantitative Alpha
    # Components:
    # - EMA Ribbon Alignment (30%)
    # - RSI Momentum (20%)
    # - MACD Histogram Momentum (20%)
    # - SuperTrend Trend Direction (15%)
    # - Stochastic Momentum (15%)
    macd_normalized = np.sign(df['macd_hist']) * np.minimum(df['macd_hist'].abs() / (df['atr_14'] + 1e-9), 1.0)

    composite_alpha = (
        (df['ema_confluence'] * 0.30) +
        (df['rsi_score'] * 0.20) +
        (macd_normalized * 0.20) +
        (df['supertrend_direction'] * 0.15) +
        (df['stoch_score'] * 0.15)
    )
    df['technical_score'] = np.clip(composite_alpha, -1.0, 1.0)

    # Confluence Ratio (% of indicators currently bullish)
    indicators_bullish = (
        (df['ema_confluence'] > 0).astype(int) +
        (df['rsi_score'] > 0).astype(int) +
        (df['macd_hist'] > 0).astype(int) +
        (df['supertrend_direction'] > 0).astype(int) +
        (df['stoch_score'] > 0).astype(int)
    )
    df['confluence_ratio'] = (indicators_bullish / 5.0) * 100.0

    return df


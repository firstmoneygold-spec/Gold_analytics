import numpy as np
import pandas as pd

def calculate_technical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate comprehensive technical indicators on OHLCV dataframe.
    Input df requires: 'open', 'high', 'low', 'close', 'volume'
    """
    df = df.copy()
    close = df['close']
    high = df['high']
    low = df['low']

    # 1. Exponential Moving Averages (EMA)
    df['ema_9'] = close.ewm(span=9, adjust=False).mean()
    df['ema_21'] = close.ewm(span=21, adjust=False).mean()
    df['ema_50'] = close.ewm(span=50, adjust=False).mean()
    df['ema_200'] = close.ewm(span=200, adjust=False).mean()

    # EMA Trend Alignment (Golden cross / Death cross)
    df['ema_trend'] = np.where(df['ema_9'] > df['ema_21'], 1, -1)

    # 2. Relative Strength Index (RSI 14)
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    df['rsi_14'] = 100 - (100 / (1 + rs))

    # 3. MACD (12, 26, 9)
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    df['macd_line'] = ema_12 - ema_26
    df['macd_signal'] = df['macd_line'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd_line'] - df['macd_signal']

    # 4. Bollinger Bands (20, 2)
    sma_20 = close.rolling(window=20).mean()
    std_20 = close.rolling(window=20).std()
    df['bb_upper'] = sma_20 + (std_20 * 2)
    df['bb_middle'] = sma_20
    df['bb_lower'] = sma_20 - (std_20 * 2)
    df['bb_bandwidth'] = (df['bb_upper'] - df['bb_lower']) / (sma_20 + 1e-9)

    # 5. Average True Range (ATR 14) for dynamic volatility stops
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df['atr_14'] = tr.rolling(window=14).mean()

    # 6. SuperTrend Indicator (10, 3)
    multiplier = 3.0
    atr_10 = tr.rolling(window=10).mean()
    hl2 = (high + low) / 2
    upper_band = hl2 + (multiplier * atr_10)
    lower_band = hl2 - (multiplier * atr_10)

    supertrend = pd.Series(index=df.index, dtype=float)
    in_uptrend = True

    for i in range(len(df)):
        if i == 0:
            supertrend.iloc[i] = lower_band.iloc[i]
            continue

        curr_close = close.iloc[i]
        prev_close = close.iloc[i - 1]

        if curr_close > upper_band.iloc[i - 1]:
            in_uptrend = True
        elif curr_close < lower_band.iloc[i - 1]:
            in_uptrend = False

        supertrend.iloc[i] = lower_band.iloc[i] if in_uptrend else upper_band.iloc[i]

    df['supertrend'] = supertrend
    df['supertrend_direction'] = np.where(close >= supertrend, 1, -1)

    # 7. Composite Technical Polarity Score (-1.0 to +1.0)
    # Aggregating EMA (30%), RSI (25%), MACD (25%), SuperTrend (20%)
    rsi_score = np.where(df['rsi_14'] < 30, 0.8, np.where(df['rsi_14'] > 70, -0.8, (df['rsi_14'] - 50) / 25))
    macd_score = np.sign(df['macd_hist']) * np.minimum(df['macd_hist'].abs() / (df['atr_14'] + 1e-9), 1.0)
    ema_score = df['ema_trend'] * 0.7
    st_score = df['supertrend_direction'] * 0.8

    composite = (ema_score * 0.30) + (rsi_score * 0.25) + (macd_score * 0.25) + (st_score * 0.20)
    df['technical_score'] = np.clip(composite, -1.0, 1.0)

    return df

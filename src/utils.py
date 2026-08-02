def add_indicators(df_data , fast ,slow , _1h):
    #calculate EMA
    df_data["ema_fast"] = df_data["close_5m"].ewm(span=fast, adjust=False).mean()
    df_data["ema_slow"] = df_data["close_5m"].ewm(span=slow, adjust=False).mean()
    df_data["ema_1h"] = df_data["close_1h"].ewm(span=_1h, adjust=False).mean()
    #calculate RSI
    delta = df_data["close_5m"].diff()
    # 1. define period
    period = 14
    # 2. Separate gains and losses
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    # 3. Calculate initial Exponential Weighted Moving Averages (EWMA)
    # Wilder's smoothing corresponds to alpha = 1 / period
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    # 4. Calculate Relative Strength (RS)
    rs = avg_gain / avg_loss
    # 5.Calculate RSI and handle division by zero
    df_data["RSI"] = 100 - (100 / (1 + rs))

    return df_data
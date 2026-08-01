import src.loader as loader
import pandas as pd

def process(df_5m ,df_1h):
    df_1h["ema_1h"] = df_1h["close"].ewm(span=13, adjust=False).mean()
    rows = []

    for _, candle_5m in df_5m.iterrows():
        current_time = candle_5m["open_time"]

        #pick out the previous 1 hour candle before current 5minute timeframe to avoid look ahead bias
        candle_1h = df_1h[df_1h["open_time"] == current_time.floor("h") - pd.Timedelta(hours=1)]
        
        #keep the 1h vacnat if data doesnt exists
        if candle_1h.empty:
            continue

        #convert to series type from dataframe
        candle_1h = candle_1h.iloc[0]

        rows.append({
            # 5minute information
                    "open_time": candle_5m["open_time"],
                    "close_time": candle_5m["close_time"],
                    "open_5m": candle_5m["open"],
                    "high_5m": candle_5m["high"],
                    "low_5m": candle_5m["low"],
                    "close_5m": candle_5m["close"],
                    
            
                    # 1H information
                    "open_1h": candle_1h["open"],
                    "high_1h": candle_1h["high"],
                    "low_1h": candle_1h["low"],
                    "close_1h": candle_1h["close"],
                    "ema_1h": candle_1h["ema_1h"]
                    
        })
    df_strategy = pd.DataFrame(rows)
    #calculate EMA
    df_strategy["ema_fast"] = df_strategy["close_5m"].ewm(span=5, adjust=False).mean()
    df_strategy["ema_slow"] = df_strategy["close_5m"].ewm(span=20, adjust=False).mean()
    
    #calculate RSI

    delta = df_strategy["close_5m"].diff()
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
    df_strategy["RSI"] = 100 - (100 / (1 + rs))
    return df_strategy

if __name__ == "__main__":
    df_5m,df_1h = loader.load_data("2023-4-6","2023-4-7")
    df_strategy = process(df_5m,df_1h)
    
    print(df_strategy)
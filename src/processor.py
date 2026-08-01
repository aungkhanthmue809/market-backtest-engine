 #still dont know what pylance did here
import pandas as pd

def process(df_5m ,df_1h):
    df_1h["ema_1h"] = df_1h["close"].ewm(span=13, adjust=False).mean()

    df_5m["lookup_1h_time"] = df_5m["open_time"].dt.floor("h") - pd.Timedelta(hours=1)

        # Rename 1h columns to avoid conflicts
    df_1h = df_1h.rename(columns={
        "open_time": "lookup_1h_time",
        "open": "open_1h",
        "high": "high_1h",
        "low": "low_1h",
        "close": "close_1h"
    })

    # Merge
    df_strategy = df_5m.merge(
        df_1h[
            [
                "lookup_1h_time",
                "open_1h",
                "high_1h",
                "low_1h",
                "close_1h",
                "ema_1h"
            ]
        ],
        on="lookup_1h_time",
        how="left"
    )

    # Keep exact output format
    df_strategy = df_strategy.rename(columns={
        "open": "open_5m",
        "high": "high_5m",
        "low": "low_5m",
        "close": "close_5m"
    })

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
    import loader as loader
    df_5m,df_1h = loader.load_data("2023-4-6","2023-4-7")
    df_strategy = process(df_5m,df_1h)
    
    print(df_strategy)
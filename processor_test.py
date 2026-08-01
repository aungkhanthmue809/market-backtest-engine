import pandas as pd
import src.loader as loader

df_5m, df_1h = loader.load_data(start_date="2023-03-04", end_date="2023-03-15")

# Ensure datetime
df_5m["open_time"] = pd.to_datetime(df_5m["open_time"])
df_1h["open_time"] = pd.to_datetime(df_1h["open_time"])

# EMA
df_1h["ema_1h"] = df_1h["close"].ewm(span=13, adjust=False).mean()

# Create the exact timestamp your loop searches for:
# 5m candle time -> previous 1h candle open time
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

# Remove rows where 1h candle doesn't exist (same as your continue)
df_strategy = df_strategy.dropna(subset=["ema_1h"])

print(df_strategy.iloc[50])
#strategy constants

LOOK_BACK = 2
def ema_rsi_strategy(df_data ,i,rsi_threshold):
        
        candle_0 = df_data.iloc[i - 2]  # Previous
        candle_1 = df_data.iloc[i -1]      # previous
        candle_2 = df_data.iloc[i]  #current
        ema_crossed_up = (candle_0["ema_fast"] <= candle_0["ema_slow"]) and (candle_1["ema_fast"] > candle_1["ema_slow"])
        ema_crossed_down = (candle_0["ema_fast"] >= candle_0["ema_slow"]) and (candle_1["ema_fast"] < candle_1["ema_slow"])

        is_bullish_1h = candle_1["close_1h"] > candle_1["ema_1h"]
        buy_condition = ema_crossed_up and (candle_1["RSI"] > rsi_threshold) and is_bullish_1h
        sell_condition = ema_crossed_down 

        return buy_condition ,sell_condition
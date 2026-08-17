import src.utils as utils

def ema_rsi_strategy(df_data ,i, parameters):
        df_data = utils.add_ema_rsi(df_data, parameters["ema_rsi"]["ema_fast"],
                                     parameters["ema_rsi"]["ema_slow"], 
                                     parameters["ema_rsi"]["ema_1h"]
                                     )
        
        rsi_threshold = parameters["ema_rsi"]["rsi_threshold"]
        candle_0 = df_data.iloc[i - 2]  # Previous
        candle_1 = df_data.iloc[i -1]      # previous
        candle_2 = df_data.iloc[i]  #current
        ema_crossed_up = (candle_0["ema_fast"] <= candle_0["ema_slow"]) and (candle_1["ema_fast"] > candle_1["ema_slow"])
        ema_crossed_down = (candle_0["ema_fast"] >= candle_0["ema_slow"]) and (candle_1["ema_fast"] < candle_1["ema_slow"])

        is_bullish_1h = candle_1["close_htf"] > candle_1["ema_htf"]
        buy_condition = ema_crossed_up and (candle_1["RSI"] > rsi_threshold) and is_bullish_1h
        sell_condition = ema_crossed_down 

        return buy_condition ,sell_condition
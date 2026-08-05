# Strategy constants

LOOK_BACK = 15

def market_structure_strategy(df_data, i):

    highs = []
    lows = []
    if i < LOOK_BACK + 2:
        return False,False
    
    # Detect pivot highs/lows in the recent window
    for j in range(i - LOOK_BACK, i - 2):
        if (
            df_data.iloc[j]["high_5m"] > df_data.iloc[j - 1]["high_5m"]
            and df_data.iloc[j]["high_5m"] > df_data.iloc[j + 1]["high_5m"]
            and df_data.iloc[j]["high_5m"] > df_data.iloc[j + 2]["high_5m"]
            and df_data.iloc[j]["high_5m"] > df_data.iloc[j - 2 ]["high_5m"]
        ):
            highs.append(df_data.iloc[j])

        if (
            df_data.iloc[j]["low_5m"] < df_data.iloc[j - 1]["low_5m"]
            and df_data.iloc[j]["low_5m"] < df_data.iloc[j + 1]["low_5m"]
            and df_data.iloc[j]["low_5m"] < df_data.iloc[j + 2]["low_5m"]
            and df_data.iloc[j]["low_5m"] < df_data.iloc[j - 2]["low_5m"]
        ):
            lows.append(df_data.iloc[j])

    #______Need at least two swing highs and lows
    if len(highs) < 2 or len(lows) < 2:
        return False, False

    #______python gimmick which allows reverse indexing
    previous_high = highs[-2]
    current_high = highs[-1]

    previous_low = lows[-2]
    current_low = lows[-1]

    #either higher high or higher low
    higher_high = current_high["high_5m"] > previous_high["high_5m"]
    higher_low = current_low["low_5m"] > previous_low["low_5m"]

    #either lower high or lower low
    lower_high = current_high["high_5m"] < previous_high["high_5m"]
    lower_low = current_low["low_5m"] < previous_low["low_5m"]

    last_before_trade = df_data.iloc[i - 1]

    is_bullish_1h = (last_before_trade["close_1h"] > last_before_trade["ema_1h"])
    
    buy_condition = (
        higher_high
        and higher_low
        #makes sure last candle close is above current high before buy(bull market)
        and last_before_trade["close_5m"] > current_high["high_5m"]
        and is_bullish_1h
    )

    sell_condition = (
        lower_high
        and lower_low
        #makes sure last candle close is below current low before buy(bear market)
        and last_before_trade["close_5m"] < current_low["low_5m"]
    )

    return buy_condition, sell_condition
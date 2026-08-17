import numpy as np

def pivot_masks(high , low , swing_window):
    n = len(high)
    pivot_high = np.ones(n ,dtype=bool)
    pivot_low = np.ones(n ,dtype=bool)

    pivot_high[:swing_window] = False
    pivot_low[:swing_window] = False

    pivot_high[n - swing_window:] = False
    pivot_low[n - swing_window:] = False

    valid_high = high[swing_window : n - swing_window ]
    valid_low = low[swing_window : n - swing_window ]

    for k in range( 1 , swing_window + 1):

        left_high = high[swing_window - k: n - swing_window - k]
        right_high = high[swing_window + k: n - swing_window + k]

        left_low = low[swing_window - k: n - swing_window - k]
        right_low = low[swing_window + k: n - swing_window + k]

        is_lower = (valid_low < left_low) &  (valid_low < right_low)
        is_higher = (valid_high > left_high) &  (valid_high > right_high)

        pivot_high[swing_window:n-swing_window] &= is_higher
        pivot_low[swing_window:n-swing_window] &= is_lower

    return pivot_high , pivot_low

def build_swings(high, low, pivot_high, pivot_low):

    #store pivot high/low as list of tuples with their corresponding candle index
    events = [(i, "h") for i in np.nonzero(pivot_high)[0]]
    events += [(i, "l") for i in np.nonzero(pivot_low)[0]]
    events.sort(key=lambda e: e[0])

    idxs = []
    kinds = []

    for i, kind in events:
        #skip same candle showing up twice as different kinds
        # which can happen if the wicks is too long
        if idxs and i == idxs[-1]:
            continue
        #when consecutive high or low occurs
        #replace the old candle if its higher or lower than the current one 
        if kinds and kind == kinds[-1]:
            if kind == "h" and high[i] > high[idxs[-1]]:
                idxs[-1] = i
            elif kind == "l" and low[i] < low[idxs[-1]]:
                idxs[-1] = i

        #append if no edge cases
        else:
            idxs.append(i)
            kinds.append(kind)

    return np.array(idxs, dtype=int), np.array(kinds)


def market_structure_strategy(df_data, i, parameters):

    attrs = df_data.attrs

    #define cache key as a tuple of parameters
    cache_key = (
        "market_structure",
        parameters["market_structure"]["look_back"],
        parameters["market_structure"]["swing_window"],
        parameters["market_structure"]["swing_count"]
    )

    #calculate and add values if not in attrs
    if cache_key not in attrs:
        look_back = parameters["market_structure"]["look_back"]
        swing_window = parameters["market_structure"]["swing_window"]
        swing_count = parameters["market_structure"]["swing_count"]
        high = df_data["high_ltf"].to_numpy(dtype=float)
        low = df_data["low_ltf"].to_numpy(dtype=float)
        close = df_data["close_ltf"].to_numpy(dtype=float)
        pivot_high, pivot_low = pivot_masks(high, low, swing_window)
        idxs, kinds = build_swings(high, low, pivot_high, pivot_low)
        #add cache key value pair to attribute
        attrs[cache_key] = (look_back, swing_window, swing_count, high, low, close, idxs, kinds)

    #unpack tuple of cache if its already cached
    look_back, swing_window, swing_count, high, low, close, idxs, kinds = attrs[cache_key]

    if i < look_back + swing_window:
        return False, False

    window_start = i - look_back
    window_end = i - 1 - swing_window
     
    if window_end < window_start:
        return False, False

    #picks out actual processed pivots we will check
    start = np.searchsorted(idxs, window_start, side="left")
    end = np.searchsorted(idxs, window_end, side="right")

    if end - start < swing_count:
        return False, False

    win_idxs = idxs[start:end]
    win_kinds = kinds[start:end]

    h_pos = np.nonzero(win_kinds == "h")[0]
    l_pos = np.nonzero(win_kinds == "l")[0]
    
    if len(h_pos) < 2 or len(l_pos) < 2:
        return False, False

    cur_high = high[win_idxs[h_pos[-1]]]
    prev_high = high[win_idxs[h_pos[-2]]]
    cur_low = low[win_idxs[l_pos[-1]]]
    prev_low = low[win_idxs[l_pos[-2]]]

    higher_high = cur_high > prev_high
    higher_low = cur_low > prev_low
    lower_high = cur_high < prev_high
    lower_low = cur_low < prev_low

    last_close = close[i - 1]

    buy_condition = higher_high and higher_low and last_close > cur_high
    sell_condition = lower_high and lower_low and last_close < cur_low

    return buy_condition, sell_condition
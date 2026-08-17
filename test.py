import numpy as np
import pandas as pd
swing_window = 2

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
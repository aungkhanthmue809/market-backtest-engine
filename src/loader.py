import pandas as pd
import glob
import random
from pathlib import Path
def load_data(start_date , end_date):
    BASE_DIR = Path(__file__).resolve().parent.parent

    _5m = glob.glob(str(BASE_DIR / "data_shelf/5m/*.csv"))
    _1h = glob.glob(str(BASE_DIR / "data_shelf/1h/*.csv"))

    columns = [
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_volume",
        "trades",
        "taker_buy_volume",
        "taker_buy_quote_volume",
        "ignore"
    ]
    numeric_cols = ["open", "high", "low", "close", "volume"]

    #gather all files into a list of dataframes
    dfs_5m = []
    for file in _5m:
        df= pd.read_csv(file, header=None, names=columns)
        dfs_5m.append(df)
    df_5m = pd.concat(dfs_5m , ignore_index=True)

    dfs_1h = []
    for file in _1h:
        df= pd.read_csv(file, header=None, names=columns)
        dfs_1h.append(df)
    df_1h = pd.concat(dfs_1h ,ignore_index=True)
        
    #unit conversion for proper calculations and dispaly
    df_1h["open_time"] = pd.to_datetime(df_1h["open_time"] ,unit="ms")
    df_5m["open_time"] = pd.to_datetime(df_5m["open_time"] ,unit="ms")
    df_1h["close_time"] = pd.to_datetime(df_1h["close_time"] ,unit="ms")
    df_5m["close_time"] = pd.to_datetime(df_5m["close_time"] ,unit="ms")

    #clear not needed
    df_1h = df_1h[["open_time","close_time" ,"open", "high", "low", "close", "volume"]]
    df_5m = df_5m[["open_time","close_time" , "open", "high", "low", "close", "volume"]]

    
    #start_date = input("enter startdate")
    #end_date = input("enter enddate") + " 23:59:59"
    mask_5m = (df_5m["open_time"] >= start_date) & (df_5m["open_time"] <= ( end_date + " 23:59:59"))
    filtered_df_5m = df_5m.loc[mask_5m]


    mask_1h = (df_1h["open_time"] >= start_date) & (df_1h["open_time"] <=( end_date + " 23:59:59"))
    filtered_df_1h = df_1h.loc[mask_1h]

    filtered_df_5m = filtered_df_5m.sort_values("open_time").reset_index(drop=True)
    filtered_df_1h = filtered_df_1h.sort_values("open_time").reset_index(drop=True)
    
    return filtered_df_5m,filtered_df_1h







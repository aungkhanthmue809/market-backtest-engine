import pandas as pd
import glob
import random
from pathlib import Path

def load_data(start_date , end_date):
    BASE_DIR = Path(__file__).resolve().parent.parent

    _ltf = glob.glob(str(BASE_DIR / "data_shelf/ltf/*.csv"))
    _htf = glob.glob(str(BASE_DIR / "data_shelf/htf/*.csv"))

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
    dfs_ltf = []
    for file in _ltf:
        df= pd.read_csv(file, header=None, names=columns)
        dfs_ltf.append(df)
    df_ltf = pd.concat(dfs_ltf , ignore_index=True)

    dfs_htf = []
    for file in _htf:
        df= pd.read_csv(file, header=None, names=columns)
        dfs_htf.append(df)
    df_htf = pd.concat(dfs_htf ,ignore_index=True)

    #format to fit vconversion
    for df in [df_htf, df_ltf]:
        for col in ["open_time", "close_time"]:
            df[col] = df[col].astype("int64")
            df.loc[df[col] >= 10**15, col] //= 1000

    #unit conversion for proper calculations and dispaly
    df_htf["open_time"] = pd.to_datetime(df_htf["open_time"] ,unit="ms")
    df_ltf["open_time"] = pd.to_datetime(df_ltf["open_time"] ,unit="ms")
    df_htf["close_time"] = pd.to_datetime(df_htf["close_time"] ,unit="ms")
    df_ltf["close_time"] = pd.to_datetime(df_ltf["close_time"] ,unit="ms")

    #clear not needed
    df_htf = df_htf[["open_time","close_time" ,"open", "high", "low", "close", "volume"]]
    df_ltf = df_ltf[["open_time","close_time" , "open", "high", "low", "close", "volume"]]

    
    #start_date = input("enter startdate")
    #end_date = input("enter enddate") + " 23:59:59"
    mask_ltf = (df_ltf["open_time"] >= start_date) & (df_ltf["open_time"] <= ( end_date + " 23:59:59"))
    filtered_df_ltf = df_ltf.loc[mask_ltf]


    mask_htf = (df_htf["open_time"] >= start_date) & (df_htf["open_time"] <=( end_date + " 23:59:59"))
    filtered_df_htf = df_htf.loc[mask_htf]

    filtered_df_ltf = filtered_df_ltf.sort_values("open_time").reset_index(drop=True)
    filtered_df_htf = filtered_df_htf.sort_values("open_time").reset_index(drop=True)
    
    return filtered_df_ltf,filtered_df_htf


if __name__ == "__main__":
    start_date = input("Enter start date (YYYY-MM-DD): ")
    end_date = input("Enter end date (YYYY-MM-DD): ")
    start_date = "2023-04-06"
    end_date = "2023-05-07"  
    df_ltf, df_htf = load_data(start_date, end_date)
    
    print("5-minute data:")
    print(df_ltf.head())
    print("\n1-hour data:")
    print(df_htf.head())






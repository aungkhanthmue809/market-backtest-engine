import pandas as pd

def process(df_ltf ,df_htf):
    
    df_ltf["lookup_htf_time"] = df_ltf["open_time"].dt.floor("h") - pd.Timedelta(hours=1)

        # Rename htf columns to avoid conflicts
    df_htf = df_htf.rename(columns={
        "open_time": "lookup_htf_time",
        "open": "open_htf",
        "high": "high_htf",
        "low": "low_htf",
        "close": "close_htf"
    })

    # Merge
    df_strategy = df_ltf.merge(
        df_htf[
            [
                "lookup_htf_time",
                "open_htf",
                "high_htf",
                "low_htf",
                "close_htf"
                
            ]
        ],
        on="lookup_htf_time",
        how="left"
    )

    df_strategy = df_strategy.dropna(subset=["close_htf"])

    # Keep exact output format
    df_strategy = df_strategy.rename(columns={
        "open": "open_ltf",
        "high": "high_ltf",
        "low": "low_ltf",
        "close": "close_ltf"
    })

    return df_strategy

if __name__ == "__main__":
    import loader as loader
    df_ltf,df_htf = loader.load_data("2023-4-6","2023-4-7")
    df_strategy = process(df_ltf,df_htf)
    
    print(df_strategy.iloc[50])
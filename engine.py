import src.loader as loader
import src.processor as processor
import matplotlib.pyplot as plt
import src.utils as utils
from pathlib import Path
import downloader as downloader
import pandas as pd
import json
import src.strategies.ema_rsi as ema_rsi
import src.strategies.market_structure as market_structure
import src.strategies.supertrend as supertrend
from tqdm import tqdm
import sys

"""
def check_data():
    
    five_min = Path("data_shelf/5m")
    one_hour = Path("data_shelf/1h")

    five_min_exists = five_min.exists() and any(five_min.glob("*.csv"))
    one_hour_exists = one_hour.exists() and any(one_hour.glob("*.csv"))

    if not five_min_exists or not one_hour_exists:
        print("No market data found. Downloading...")
        downloader.download_data()
    else:
        print("Market data found")
"""
def calculate(start_date, end_date, config):
#_____adding variables
    fee_rate = config["global"]["fee_rate"]
    slippage = config["global"]["slippage"]
    initial_balance = config["global"]["initial_balance"]
    fast = config["strategy"]["parameters"]["fast"]
    slow = config["strategy"]["parameters"]["slow"]
    ema_1h = config["strategy"]["parameters"]["ema_1h"]
    rsi_threshold = config["strategy"]["parameters"]["rsi_threshold"]
    strategy = config["strategy"]["name"]

    df_5m, df_1h = loader.load_data(start_date, end_date)
    df_data = processor.process(df_5m, df_1h)
    
    total_trades = 0
    in_position = False

    final_balance = initial_balance
    balance_history = [final_balance]
    time_history = [df_data.iloc[2]["open_time"]]

    profit = 0
    entry_price = 0

    winning_trades = 0
    losing_trades = 0

    gross_profit = 0
    gross_loss = 0

    peak_balance = initial_balance
    max_drawdown = 0.0

    df_data = utils.add_ema_rsi(df_data, fast, slow, ema_1h)
    
#checking strategy
    if (strategy) == "ema_rsi": 
        look_back = ema_rsi.LOOK_BACK
    elif (strategy) == "market_structure": 
        look_back = market_structure.LOOK_BACK
    elif (strategy) == "supertrend": 
        look_back = supertrend.LOOK_BACK


#_____TRADING LOGIC LOOP
    for i in tqdm(
        range(look_back, len(df_data)),
        desc=f"Backtesting {strategy}",
        unit="candle",
        disable=not sys.stdout.isatty()
    ):
        #if pd.isna(candle_1["ema_1h"]):
        #           continue
        #print("boo")
        #print(candle_0, candle_1 , df_data.iloc[i])
        
        if (strategy) == "ema_rsi": 
                buy_condition , sell_condition = ema_rsi.ema_rsi_strategy(df_data ,i ,rsi_threshold)
        elif (strategy) == "market_structure": 
                buy_condition , sell_condition = market_structure.market_structure_strategy(df_data ,i )
        elif (strategy) == "supertrend": 
                buy_condition , sell_condition = supertrend.supertrend_strategy(df_data ,i ,rsi_threshold)

        if buy_condition and not in_position :
            #The buying
            entry_price = df_data.iloc[i]["open_5m"]* (1 + slippage)

            #print(f"entry price: {entry_price}")
            in_position = True

        elif sell_condition and in_position :#and not is_bullish_1h:
            #THE selling
            exit_price = df_data.iloc[i]["open_5m"] * (1 - slippage)

            #print(f"exit price: {exit_price}")

            #profit_percent =  (exit_price/ (entry_price/100) ) - 100
            #profit = ((final_balance/100) * profit_percent)

            #calculate PROfit better right way (special number means percentage described as x/100 eg. 20% as 0.20 in code)
            #get trade return in special form by removing 100 from percent increase formula
            trade_return = (exit_price - entry_price) / entry_price
            #get fee in the special form and subtract from trade return since both in special form
            fees = fee_rate * 2
            net_return = trade_return - fees
            #change the net_return which is profit percent in special form into number form eg. 0.20 to 20%
            profit_percent = net_return * 100
            #calcualte profit amount using speical number which can be used to fnid percentage directly just by multiplying
            profit = final_balance * net_return
            final_balance += profit

            in_position = False
            total_trades+=1
            if profit_percent > 0:
                winning_trades+=1
                gross_profit += profit
            elif profit_percent < 0:
                losing_trades+=1
                gross_loss -= profit
            balance_history.append(final_balance)
            if final_balance > peak_balance:
                peak_balance = final_balance

            drawdown = ((peak_balance - final_balance) / peak_balance) * 100

            if drawdown > max_drawdown:
                max_drawdown = drawdown
                        
            time_history.append(df_data.iloc[i]["open_time"])
        
    if in_position:
        # sell at the last candle
        exit_price = df_data.iloc[-1]["open_5m"] * (1 - slippage)

        print(f"final exit price: {exit_price}")

        trade_return = (exit_price - entry_price) / entry_price

        fees = fee_rate * 2
        net_return = trade_return - fees

        profit_percent = net_return * 100

        profit = final_balance * net_return
        final_balance += profit

        in_position = False
        total_trades += 1

        if profit_percent > 0:
            winning_trades += 1
            gross_profit += profit
        elif profit_percent < 0:
            losing_trades += 1
            gross_loss -= profit

        balance_history.append(final_balance)
        time_history.append(df_data.iloc[-1]["open_time"])

        if final_balance > peak_balance:
            peak_balance = final_balance

        drawdown = ((peak_balance - final_balance) / peak_balance) * 100

        if drawdown > max_drawdown:
            max_drawdown = drawdown
    #plt.figure(figsize=(12, 6))
    #plt.plot(time_history, balance_history, marker='o', linestyle='-', color='b')
    #plt.title('Backtest data Balance Over Time')
    #plt.xlabel('Time')
    #plt.ylabel('Balance')
    #plt.tight_layout()
    #plt.show()
    #print(final_balance)
    
    stats = {
        "initial_balance": initial_balance,
        "final_balance": final_balance,
        "net_profit": final_balance - initial_balance,
        "return_percent": ((final_balance / initial_balance) - 1) * 100,

        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "win_rate": (winning_trades / total_trades) * 100 if total_trades else 0,
        "gross_profit" : gross_profit,
        "gross_loss" : gross_loss,
        "average_winning_trade": gross_profit / winning_trades if winning_trades else 0,
        "average_losing_trade": gross_loss / losing_trades if losing_trades else 0,

        "maximum_drawdown": max_drawdown
    }
    
    return time_history, balance_history, stats

if __name__ == "__main__":
    with open("config.json", "r") as f:
        config = json.load(f)
    times, balances, stats = calculate(
        "2023-04-06",
        "2024-05-07",
        config
    )
    print(stats)

    
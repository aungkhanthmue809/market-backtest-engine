import src.loader as loader
import src.processor as processor
import matplotlib.pyplot as plt
import src.utils as utils
from pathlib import Path
import downloader as downloader
import pandas as pd
import json
import time
import src.strategies.ema_rsi as ema_rsi
import src.strategies.market_structure as market_structure
from tqdm import tqdm

def calculate(start_date, end_date, config, parameters=None, df_data=None):
    #important to include none
    if parameters is None:
        with open("parameters.json", "r") as f:
            parameters = json.load(f)
    
    fee_rate = config["global"]["fee_rate"]
    slippage = config["global"]["slippage"]
    initial_balance = config["global"]["initial_balance"]
    strategy = config["strategy"]
    rr_ratio = parameters["market_structure"]["rr_ratio"] 

#checking strategy and passing parameters
    if (strategy) == "ema_rsi": 
        look_back = parameters["ema_rsi"]["look_back"]

    elif (strategy) == "market_structure": 
        look_back = parameters["market_structure"]["look_back"]
        
    if df_data is None:
        df_ltf, df_htf = loader.load_data(start_date, end_date)
        df_data = processor.process(df_ltf, df_htf)
    
    total_trades = 0
    in_position = False

    #pull price columns into numpy arrays once; iloc row access inside the loop is very slow
    open_ltf = df_data["open_ltf"].to_numpy(dtype=float)
    high_ltf = df_data["high_ltf"].to_numpy(dtype=float)
    low_ltf = df_data["low_ltf"].to_numpy(dtype=float)
    open_time = df_data["open_time"].to_numpy()

    final_balance = initial_balance
    balance_history = [final_balance]
    time_history = [open_time[look_back]]
    sl = 0
    tp = 0
    profit = 0
    entry_price = 0

    winning_trades = 0
    losing_trades = 0

    gross_profit = 0
    gross_loss = 0

    peak_balance = initial_balance
    max_drawdown = 0.0
    
#_____TRADING LOGIC LOOP
    for i in tqdm(
        range(look_back+1, len(df_data)),
        desc=f"Backtesting {strategy}",
        unit="candle",
    ):
        
        if (strategy) == "ema_rsi": 
                buy_condition , sell_condition = ema_rsi.ema_rsi_strategy(df_data ,i ,parameters)
        elif (strategy) == "market_structure": 
                buy_condition , sell_condition = market_structure.market_structure_strategy(df_data ,i ,parameters)

        if (buy_condition and not in_position)  :
            #The buying
            entry_price = open_ltf[i] * (1 + slippage)

            risk =  entry_price * 0.02
            reward = risk * rr_ratio
            sl = entry_price - risk
            tp = entry_price + reward
            #print(f"entry price: {entry_price}")
            in_position = True

        elif in_position:

            high = high_ltf[i]
            low = low_ltf[i]
            open_price = open_ltf[i]

            exit_price = None

            if low <= sl:
                exit_price = sl * (1 - slippage)

            elif high >= tp:
                exit_price = tp * (1 - slippage)

            elif sell_condition:
                exit_price = open_price * (1 - slippage)

            if exit_price is not None:

                trade_return = (exit_price - entry_price) / entry_price

                fees = fee_rate * 2
                net_return = trade_return - fees

                profit_percent = net_return * 100
                profit = final_balance * net_return
                final_balance += profit

                in_position = False

                total_trades += 1

                if profit_percent >= 0:
                    winning_trades += 1
                    gross_profit += profit
                else:
                    losing_trades += 1
                    gross_loss -= profit

                balance_history.append(final_balance)

                if final_balance > peak_balance:
                    peak_balance = final_balance

                drawdown = ((peak_balance - final_balance) / peak_balance) * 100

                if drawdown > max_drawdown:
                    max_drawdown = drawdown

                time_history.append(open_time[i])
    if in_position:
        # sell at the last candle
        exit_price = open_ltf[-1] * (1 - slippage)

        print(f"final exit price: {exit_price}")

        trade_return = (exit_price - entry_price) / entry_price

        fees = fee_rate * 2
        net_return = trade_return - fees

        profit_percent = net_return * 100

        profit = final_balance * net_return
        final_balance += profit

        in_position = False
        total_trades += 1

        if profit_percent >= 0:
            winning_trades += 1
            gross_profit += profit
        elif profit_percent < 0:
            losing_trades += 1
            gross_loss -= profit

        balance_history.append(final_balance)
        time_history.append(open_time[-1])

        if final_balance > peak_balance:
            peak_balance = final_balance

        drawdown = ((peak_balance - final_balance) / peak_balance) * 100

        if drawdown > max_drawdown:
            max_drawdown = drawdown

    stats = {
        "parameters" : parameters[strategy],
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
    #print(stats)
    return time_history, balance_history, stats

if __name__ == "__main__":
    with open("config.json", "r") as f:
        config = json.load(f)

    start_date = "2024-04-06"
    end_date = "2026-05-07"

    start = time.time()
    times, balances, stats = calculate(
        start_date,
        end_date,
        config
    )
    elapsed_time = time.time() - start
    

    results_file = "results/backtest_results.json"

    new_result = {
        "start_date": start_date,
        "end_date": end_date,
        "time_taken_seconds": round(elapsed_time, 2),
        "statistics": stats
    }

    try:
        with open(results_file, "r") as file:
            old_results = json.load(file)

        if isinstance(old_results, dict):
            old_results = [old_results]

    except (FileNotFoundError, json.JSONDecodeError):
        old_results = []

    old_results.append(new_result)
    old_results = old_results[-10:]

    with open(results_file, "w") as file:
        json.dump(old_results, file, indent=4)

    print(f"Results appended to {results_file}")
    print(new_result)

    
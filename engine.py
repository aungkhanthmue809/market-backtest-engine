import src.loader as loader
import src.processor as processor
import matplotlib.pyplot as plt


def calculate(start_date, end_date, config):
    df_5m, df_1h = loader.load_data(start_date, end_date)
    df_data = processor.process(df_5m, df_1h)

    fee_rate = config["fee_rate"]
    slippage = config["slippage"]
    initial_balance = config["initial_balance"]

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

    for i in range(2, len(df_data) ):
        candle_0 = df_data.iloc[i - 2]  # Previous
        candle_1 = df_data.iloc[i -1]      # previous
        candle_2 = df_data.iloc[i]  #current

        #print("boo")
        #print(candle_0, candle_1 , candle_2)
        
        ema_crossed_up = (candle_0["ema_fast"] <= candle_0["ema_slow"]) and (candle_1["ema_fast"] > candle_1["ema_slow"])
        ema_crossed_down = (candle_0["ema_fast"] >= candle_0["ema_slow"]) and (candle_1["ema_fast"] < candle_1["ema_slow"])

        is_bullish_1h = candle_1["close_1h"] > candle_1["ema_1h"]

        if ema_crossed_up and (candle_1["RSI"] > 60) and not in_position :#and is_bullish_1h:
            #The buying
            entry_price = candle_2["open_5m"]* (1 + slippage)

            print(f"entry price: {entry_price}")
            in_position = True

        elif ema_crossed_down and in_position :#and not is_bullish_1h:
            #THE selling
            exit_price = candle_2["open_5m"] * (1 - slippage)

            print(f"exit price: {exit_price}")

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
                        
            time_history.append(candle_2["open_time"])

    #plt.figure(figsize=(12, 6))
    #plt.plot(time_history, balance_history, marker='o', linestyle='-', color='b')
    #plt.title('Backtest Strategy Balance Over Time')
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

    times, balances, stats = calculate(
        "2023-04-06",
        "2024-05-07"
    )

    print(stats)
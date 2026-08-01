import loader
import processor
import matplotlib.pyplot as plt
import time

start = time.time()
df_5m ,df_1h = loader.load_data("2020-4-6","2026-5-7")
df_data = processor.process(df_5m,df_1h)
#print(df_5m)
#print(df_1h)
#x = "2023-4-6 4:00:00"
#y = "2023-4-6 6:00:00"
in_position = False
trade_count = 0
initial_balance = 1000
final_balance = initial_balance
balance_history = [final_balance]
time_history = [df_data.iloc[2]["open_time"]]
profit = 0
entry_price = 0

for i in range(2, len(df_data) ):
    candle_0 = df_data.iloc[i - 2]  # Previous
    candle_1 = df_data.iloc[i -1]      # previous
    candle_2 = df_data.iloc[i]  #current

    #print("boo")
    #print(candle_0, candle_1 , candle_2)
    
    ema_crossed_up = (candle_0["ema_fast"] <= candle_0["ema_slow"]) and (candle_1["ema_fast"] > candle_1["ema_slow"])
    ema_crossed_down = (candle_0["ema_fast"] >= candle_0["ema_slow"]) and (candle_1["ema_fast"] < candle_1["ema_slow"])

    is_bullish_1h = candle_1["close_1h"] > candle_1["ema_1h"]

    if ema_crossed_up and (candle_1["RSI"] > 60) and not in_position and is_bullish_1h:
        entry_price = candle_2["open_5m"]
        print(f"entry price: {entry_price}")
        in_position = True

    elif ema_crossed_down and in_position :#and not is_bullish_1h:
        exit_price = candle_2["open_5m"]
        print(f"exit price: {exit_price}")
        profit_percent =  (exit_price/ (entry_price/100) ) - 100
        
        final_balance = final_balance + ((final_balance/100) * profit_percent)
        in_position = False
        balance_history.append(final_balance)
        time_history.append(candle_2["open_time"])
        trade_count += 1

if in_position:
    exit_price = df_data.iloc[-1]["close_5m"]
    profit_percent = (exit_price / entry_price) * 100 - 100
    final_balance *= (1 + profit_percent / 100)
end = time.time()
total = end - start 
print(total) 
print(final_balance)
print("Trades:", trade_count)
plt.figure(figsize=(12, 6))
plt.plot(time_history, balance_history, marker='o', linestyle='-', color='b')
plt.title('Backtest Strategy Balance Over Time')
plt.xlabel('Time')
plt.ylabel('Balance')
plt.grid(True)
plt.tight_layout()
plt.savefig("results/balance_history.png", dpi=300)
plt.show()


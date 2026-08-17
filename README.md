# Asset Backtester

A crypto backtesting engine built around Binance's public historical data. It downloads kline data, processes it into lower and higher timeframe frames, runs a strategy over it, and shows the results in a Streamlit dashboard.

The point of this repo is the engine, not the strategies. Anyone can slot their own strategy into `src/strategies/` and run it — the downloader, loader, trade loop and reporting are all generic.

## What's inside

```
downloader.py    Pulls monthly kline zips from data.binance.vision and extracts CSVs
src/loader.py    Reads CSVs back into dataframes, handles the 15m/1h merge
src/processor.py   Builds the LTF/HTF combined frame the engine trades on
src/strategies/   Where strategy logic lives (the plug-in point)
engine.py        The main backtest loop, fills, fees/slippage, stats
optimiser.py     Grid search over strategy parameters, resume-safe
app.py           Streamlit UI
config.json      Global settings + which strategy to run
parameters.json  Per-strategy parameter values
```

## The bundled strategies

There are two strategies in `src/strategies/`:

- `ema_rsi` — EMA cross + RSI filter, with a 1h trend check
- `market_structure` — swing-high/swing-low structure breaks with RR-based SL/TP

**These are only there to demonstrate the engine works.** They are not tuned, not profitable, and you should not trade them. Treat them as examples of what a strategy module looks like. If you want a strategy worth running, write your own — or hire someone to.

## Requirements

`requirements.txt`:

```
pandas
matplotlib
requests
python-dateutil
streamlit
win11toast
tqdm
```

`win11toast` is only used for Windows notifications in the UI, so you can drop it on other OSes.

## Running it

1. `pip install -r requirements.txt`
2. `streamlit run app.py` (or just run `run.bat` on Windows)
3. Pick a symbol, hit **Download Data** — this grabs ~7 years of 15m/1h klines into `data_shelf/`
4. Hit **Run Backtest**

Or skip the UI and run the engine directly: `python engine.py`.

`data_shelf/` is gitignored, so everyone has to download their own data. That's intentional because the CSVs are large.

## Configuration

`config.json`:

```json
{
    "global": {
        "fee_rate": 0.0005,
        "slippage": 0.0002,
        "initial_balance": 1000
    },
    "strategy": "market_structure"
}
```

Switch the strategy by changing the `strategy` field. Parameter grids for the optimiser live in `optimiser.py`; defaults are in `parameters.json`.

## Writing your own strategy

Each strategy is a function that takes the combined frame and the current candle index and returns `(buy_condition, sell_condition)`:

```python
def my_strategy(df_data, i, parameters):
    buy = ...
    sell = ...
    return buy, sell
```

Then drop it into `src/strategies/`, add a branch for it in `engine.py` (where the strategy is selected), and set it in `config.json`. The optimiser needs its parameter names added to the grid. That's the whole interface.

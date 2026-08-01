# btc-backtester-demo
A Python-based cryptocurrency trading strategy backtester that analyzes Bitcoin OHLCV data using multiple timeframes.

The project processes 5-minute and 1-hour Binance candle data, calculates technical indicators, runs a trading strategy, and displays performance results through a Streamlit dashboard.

## Features

- Binance OHLCV CSV data loading
- Multi-timeframe analysis:
  - 5-minute candles for entries
  - 1-hour candles for trend filtering
- EMA crossover strategy
- RSI filtering
- Avoids look-ahead bias when using higher timeframe data
- Backtesting engine with balance tracking
- Streamlit dashboard visualization
- Balance curve display

## Project Structure

```
trading_bot/
│
├── app.py                 # Streamlit dashboard
├── run.bat                # Quick launcher for the app
├── requirements.txt       # Python dependencies
│
├── src/
│   ├── loader.py          # Data loading and preparation
│   ├── processor.py       # Indicator calculations
│   └── engine.py          # Backtesting logic
│
└── data_shelf/
    ├── 5m/                # 5-minute BTC data
    └── 1h/                # 1-hour BTC data
```

## Installation

Clone the repository:

```bash
git clone https://github.com/aungkhanthmue809/btc-backtester-demo.git
cd trading_bot
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

Start the Streamlit dashboard:

```bash
streamlit run app.py
```

or use:

```
run.bat
```

The application will open in your browser.

## Strategy Logic

The current strategy uses:

### Entry Conditions
- Fast EMA crosses above slow EMA
- RSI is above 60
- Current 1-hour trend is bullish
- No active position

### Exit Conditions
- Fast EMA crosses below slow EMA

The backtester simulates trades using candle open prices.

## Data

The project uses Binance OHLCV candle data.

Required folders:

```
data_shelf/
├── 5m/
└── 1h/
```

The included dataset contains historical Bitcoin data for testing.

## Limitations

This project is for research and educational purposes.

Current limitations:
- Does not include trading fees
- Does not include slippage
- Uses simplified trade execution
- Strategy parameters are manually selected
- Does not represent guaranteed real trading performance

## Future Improvements

Possible improvements:
- Add trade history table
- Add win rate and drawdown statistics
- Add configurable strategy parameters
- Add optimization/backtesting comparison tools
- Add more indicators and strategies

## Disclaimer

This project is not financial advice. It is a programming and quantitative research project.

import streamlit as st
import time
import json
import importlib
import engine
from win11toast import toast
import downloader

st.set_page_config(
    page_title="Assest Trading Bot Backtester",
    layout="wide"
)

st.title("Assest Trading Bot Backtester")

# Inputs
col1, col2, col3 = st.columns(3)

with col1:
    symbol = st.text_input(
        "Symbol",
        "---"
    )

with col2:
    start_date = st.text_input(
        "Start Date",
        "2023-04-06"
    )

with col3:
    end_date = st.text_input(
        "End Date",
        "2023-05-07"
    )

# Buttons
col1, col2 = st.columns(2)

with col1:
    download = st.button("Download Data", use_container_width=True)

with col2:
    run = st.button("Run Backtest", use_container_width=True)

with open("config.json", "r") as file:
    config = json.load(file)

# Download data
if download:
    importlib.reload(engine)

    with st.spinner("Downloading data..."):
        downloader.download_data(symbol)

    st.success("Data download complete!")

    toast(
        "Download Complete",
        "Historical market data has been downloaded."
    )

# Run backtest
if run:
    start = time.time()

    with st.spinner("Running backtest..."):

        importlib.reload(engine)

        times, balances, stats = engine.calculate(
            start_date,
            end_date,
            config
        )

    end = time.time()

    elapsed_time = end - start

    st.success("Finished")

    # Windows notification
    toast(
        "Backtest Complete",
        f"Finished in {elapsed_time:.2f} seconds"
    )

    # Save results
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

    # Balance graph
    st.subheader("Balance Curve")

    chart_data = {
        "Time": times,
        "Balance": balances
    }

    st.line_chart(
        chart_data,
        x="Time",
        y="Balance"
    )

    # Statistics
    st.subheader("Statistics")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Initial Balance", f"${stats['initial_balance']:.2f}")
    c2.metric("Final Balance", f"${stats['final_balance']:.2f}")
    c3.metric("Net Profit", f"${stats['net_profit']:.2f}")
    c4.metric("Return", f"{stats['return_percent']:.2f}%")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Trades", stats["total_trades"])
    c2.metric("Winning Trades", stats["winning_trades"])
    c3.metric("Losing Trades", stats["losing_trades"])
    c4.metric("Win Rate", f"{stats['win_rate']:.2f}%")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Gross Profit", f"${stats['gross_profit']:.2f}")
    c2.metric("Gross Loss", f"${stats['gross_loss']:.2f}")
    c3.metric("Average Winning Trade", f"${stats['average_winning_trade']:.2f}")
    c4.metric("Average Losing Trade", f"${stats['average_losing_trade']:.2f}")

    c1, c2 = st.columns(2)

    c1.metric("Maximum Drawdown", f"{stats['maximum_drawdown']:.2f}%")
    c2.metric("Runtime", f"{elapsed_time:.2f} seconds")
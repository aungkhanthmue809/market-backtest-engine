import streamlit as st
import time
import json
from engine import calculate


st.set_page_config(
    page_title="Trading Bot Backtester",
    layout="wide"
)


st.title("Trading Bot Backtester")


# Inputs
col1, col2 = st.columns(2)

with col1:
    start_date = st.text_input(
        "Start Date",
        "2023-04-06"
    )

with col2:
    end_date = st.text_input(
        "End Date",
        "2024-05-07"
    )


run = st.button("Run Backtest")


if run:
    start = time.time()

    with st.spinner("Running backtest..."):

        times, balances, stats = calculate(
            start_date,
            end_date
        )

    end = time.time()

    elapsed_time = end - start

    st.success("Finished")


    # Save results to JSON
    results = {
        "start_date": start_date,
        "end_date": end_date,
        "time_taken_seconds": round(elapsed_time, 2),
        "statistics": stats
    }

    with open("results/backtest_results.json", "w") as file:
        json.dump(results, file, indent=4)


    # Completion sound
    with open("done.mp3", "rb") as audio_file:
        audio_bytes = audio_file.read()

    st.audio(
        audio_bytes,
        format="audio/mp3",
        autoplay=True
    )


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
    # Statistics
    st.subheader("Statistics")

    # Row 1
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Initial Balance", f"${stats['initial_balance']:.2f}")
    c2.metric("Final Balance", f"${stats['final_balance']:.2f}")
    c3.metric("Net Profit", f"${stats['net_profit']:.2f}")
    c4.metric("Return", f"{stats['return_percent']:.2f}%")

    # Row 2
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Trades", stats["total_trades"])
    c2.metric("Winning Trades", stats["winning_trades"])
    c3.metric("Losing Trades", stats["losing_trades"])
    c4.metric("Win Rate", f"{stats['win_rate']:.2f}%")

    # Row 3
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Gross Profit", f"${stats['gross_profit']:.2f}")
    c2.metric("Gross Loss", f"${stats['gross_loss']:.2f}")
    c3.metric("Average Winning Trade", f"${stats['average_winning_trade']:.2f}")
    c4.metric("Average Losing Trade", f"${stats['average_losing_trade']:.2f}")

    # Row 4
    c1, c2 = st.columns(2)

    c1.metric("Maximum Drawdown", f"{stats['maximum_drawdown']:.2f}%")
    c2.metric("Runtime", f"{elapsed_time:.2f} seconds")
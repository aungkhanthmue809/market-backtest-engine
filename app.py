import streamlit as st

import src.loader as loader
import src.processor as processor

from src.engine import calculate


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

    with st.spinner("Running backtest..."):

        # Load
        df_5m, df_1h = loader.load_data(
            start_date,
            end_date
        )


        # Process
        df_data = processor.process(
            df_5m,
            df_1h
        )


        # Calculate
        times, balances, stats = calculate(
            df_data
        )


    st.success("Finished")


    # Graph

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


    # Stats

    st.subheader("Statistics")


    c1, c2, c3 = st.columns(3)


    c1.metric(
        "Starting Balance",
        f"${stats['initial_balance']:.2f}"
    )

    c2.metric(
        "Final Balance",
        f"${stats['final_balance']:.2f}"
    )

    c3.metric(
        "Profit %",
        f"{stats['profit_percent']:.2f}%"
    )
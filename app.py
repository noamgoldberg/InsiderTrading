from typing import Union, Tuple
import streamlit as st
import numpy as np
import pandas as pd


from open_insider.query_agent import QueryAgent

from yahoo_finance.process_data import get_ticker_trades_and_stock_data


from streamlit_app.active import (
    get_active_dataset,
    get_active_params,
    set_active_dataset_and_params
)
from streamlit_app.filters import (
    display_and_extract_filters,
    apply_filters,
    display_active_filters
)
from streamlit_app.footnotes import display_legend_footnotes
from streamlit_app.groupby_aggregate import extract_gb_and_agg, apply_gb_and_agg
from streamlit_app.plot import plot_trade_chart, plot_company_stock_and_trades



def run():
    
    # (0) Establish Parameters
    remember = 2
    max_rows = 5000
    trade_val_step = 50000
    trade_val_round = -9

    # (1) Initialize QueryAgent
    query_agent = QueryAgent(
        remember=remember, # remember data from up to 2 recent queries
        max_rows=max_rows
    )

    # (2) Initialize (Query) Default Dataset
    st.session_state["datasets"] = st.session_state.get("datasets", {
        "default": query_agent.scrape(
            trade_types=None,
            job_titles=None,
            trade_val_min=None,
            trade_val_max=None,
            num_results=max_rows,
        ),
        "filtered": None
    })

    # (3) Set Active Data & Parameters
    if st.session_state.get("active", None) is None:
        set_active_dataset_and_params(
            dataset_name="default",
            params={
                "trade_types": None,
                "job_titles": None,
                "insiders": None,
                "companies": None,
                "trade_val_min": None,
                "trade_val_max": None,
            }
        )

    # (3) Display Title & Create Tabs Popover, & Filters
    st.set_page_config(page_title="Insider Trading Visualizer", page_icon="📈")
    st.title("OpenInsider Data Analysis")
    company_insights, aggregate_insights = st.tabs(["Company Insights", "Aggregate Trends & Insights"])

    # (4) Display "Company Insights" Tab
    with company_insights:
        trading_data = st.session_state["datasets"]["default"]
        company_ticker_map = trading_data[
            ["Company Name", "Ticker"]
        ].set_index("Company Name").iloc[:, 0].drop_duplicates().to_dict()
        company = st.selectbox("Select a Company to Visualize ", options=company_ticker_map.keys(), index=None)
        if company:
            ticker = company_ticker_map[company]
            ticker_trading_data, ticker_stock_data = get_ticker_trades_and_stock_data(
                st.session_state["datasets"]["default"],
                ticker
            )
            try:
                fig = plot_company_stock_and_trades(
                    ticker_trading_data,
                    ticker_stock_data,
                    show=False
                )
                st.write(f"#### Trades & Stock Price for {company} ({ticker}) Over Time")
                st.plotly_chart(fig)
            except Exception as error:
                st.error(f"Failed to generate plot for {company} ({ticker})")
                raise error
            st.write(f"#### All Trades for {company} ({ticker})")
            st.dataframe(ticker_trading_data.sort_values("Trade Date"))
    
    # (5) Display "Aggregate Insights" Tab
    with aggregate_insights:
        st.write("#### Trade Trends & Insights")
        popover = st.popover("Filters")
        selected_filters = display_and_extract_filters(
            default_dataset=st.session_state["datasets"]["default"],
            trade_val_step=trade_val_step,
            trade_val_round=trade_val_round,
            popover=popover,
        )

        # (A) Apply Filters, Set Active Data & Parameters
        if popover.button("Apply Filters"):
            apply_filters(
                query_agent=query_agent,
                selected_filters=selected_filters,
                max_rows=max_rows,
            )

        # (B) Extract & Apply Groupby & Aggregation
        groupby, aggregation = extract_gb_and_agg()
        df_plot, x = apply_gb_and_agg(
            groupby,
            aggregation,
            get_active_dataset()
        )

        # (C) Get Top N
        top_n = None
        if groupby == "Company":
            top_n = st.slider("Show Top # Companies", min_value=5, max_value=min(df_plot.shape[0], 100), value=25, step=5)

        # (D) Plot chart
        params = get_active_params()
        display_active_filters(
            trade_types=params["trade_types"],
            job_titles=params["job_titles"],
            insiders=params["insiders"],
            companies=params["companies"],
            trade_val_min=params["trade_val_min"],
            trade_val_max=params["trade_val_max"],
        )
        plot_trade_chart(
            df_plot=df_plot,
            x=x,
            aggregation=aggregation,
            groupby=groupby,
            top_n=top_n,
        )

        df_display = get_active_dataset().copy()
        def format_dollar_amt(amt: Union[int, float], decimals: int = 2) -> str:
            sym = '-' if amt < 0 else ''
            return f"{sym}${abs(amt):,.{decimals}f}"
        df_display["Price"] = df_display["Price"].apply(lambda amt: format_dollar_amt(amt, 2) if amt not in [np.nan, None] else None)
        df_display["Value"] = df_display["Value"].apply(lambda amt: format_dollar_amt(amt, 0) if amt not in [np.nan, None] else None)
        df_display["ΔOwn"] = df_display["ΔOwn"].apply(lambda pct: f"{pct:.0%}" if pct not in [np.nan, None] else None)

        st.subheader("All Trades")
        st.dataframe(df_display)
        display_legend_footnotes()


if __name__ == "__main__":
    run()
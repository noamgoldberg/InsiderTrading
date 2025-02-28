import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

from utils.plotly_utils import create_categorical_chart, create_time_series_chart
from consts import TEMPORAL_GBS


def plot_trade_chart(
    df_plot: pd.DataFrame,
    x: str,
    aggregation: str,
    groupby: str,
    top_n: int = None
) -> go.Figure:
    """Determines the appropriate chart type and renders it."""
    title = f"{aggregation} of Trades Over Time".replace('Total of', 'Total')
    if groupby in TEMPORAL_GBS:
        fig = create_time_series_chart(
            df=df_plot,
            x=x,
            aggregation=aggregation,
            groupby=groupby,
            title=title
        )
    else:
        fig = create_categorical_chart(
            df=df_plot,
            x=x,
            aggregation=aggregation,
            groupby=groupby,
            top_n=top_n,
            title=title
        )
    st.plotly_chart(fig)
    return fig


def plot_company_stock_and_trades(
    ticker_trading_data: pd.DataFrame,
    ticker_stock_data: pd.DataFrame,
    show: bool = False
) -> go.Figure:
    # Convert date columns to datetime
    ticker_trading_data["Trade Date"] = pd.to_datetime(ticker_trading_data["Trade Date"])
    ticker_stock_data.index = pd.to_datetime(ticker_stock_data.index)
    
    # Create stock price line plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ticker_stock_data.index,
        y=ticker_stock_data['Close'],
        mode='lines',
        name='Stock Price',
        line=dict(color='blue')
    ))
    
    # Separate buy and sell trades
    buy_trades = ticker_trading_data[ticker_trading_data['Trade Type'].str.contains('B')]
    sell_trades = ticker_trading_data[ticker_trading_data['Trade Type'].str.contains('S')]
    
    min_bubble_size = 5
    
    # Add buy trades scatter plot (green bubbles)
    fig.add_trace(go.Scatter(
        x=buy_trades['Trade Date'],
        y=buy_trades['Price'],
        mode='markers',
        marker=dict(
            size=(abs(buy_trades['Value']) / 1e6).apply(lambda x: max(x, min_bubble_size)) ,  # Scale bubble size
            color='green',
            opacity=0.6
        ),
        text=buy_trades.apply(lambda row: f"Insider: {row['Insider Name']}<br>Amount: {row['Quantity']}", axis=1),
        name='Purchase'
    ))
    
    # Add sell trades scatter plot (red bubbles)
    fig.add_trace(go.Scatter(
        x=sell_trades['Trade Date'],
        y=sell_trades['Price'],
        mode='markers',
        marker=dict(
            size=(abs(sell_trades['Value']) / 1e6).apply(lambda x: max(x, min_bubble_size)) ,  # Scale bubble size
            color='red',
            opacity=0.6
        ),
        text=sell_trades.apply(lambda row: f"Insider: {row['Insider Name']}<br>Amount: {row['Quantity']}", axis=1),
        name='Sale'
    ))
    
    # Update layout
    fig.update_layout(
        title='Stock Price and Insider Trades',
        xaxis_title='Date',
        yaxis_title='Price',
        legend_title='Legend',
        template='plotly_white'
    )
    
    if show:
        fig.show()
    
    return fig
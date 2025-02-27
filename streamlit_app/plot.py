import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from core.utils.plotly_utils import create_categorical_chart, create_time_series_chart
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
            df_plot=df_plot,
            x=x,
            y=aggregation,
            groupby=groupby,
            title=title
        )
    else:
        fig = create_categorical_chart(
            df_plot=df_plot,
            x=x,
            y=aggregation,
            groupby=groupby,
            top_n=top_n,
            title=title
        )
    st.plotly_chart(fig)
    return fig
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from core.utils.plotly_utils import create_categorical_chart, create_time_series_chart
from consts import TEMPORAL_GBS


def plot_trade_chart(
    df_plot: pd.DataFrame,
    x: str,
    y: str,
    groupby: str,
    top_n: int = None
) -> go.Figure:
    """Determines the appropriate chart type and renders it."""
    if groupby in TEMPORAL_GBS:
        fig = create_time_series_chart(df_plot, x, y, groupby)
    else:
        fig = create_categorical_chart(df_plot, x, y, groupby, top_n)
    st.plotly_chart(fig)
    return fig
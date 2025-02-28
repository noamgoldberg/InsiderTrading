from typing import Tuple
import streamlit as st
import pandas as pd
import numpy as np


GROUPBY_OPTIONS_DICT = {
    "Company": ("Company Name", lambda df: df.groupby("Company Name")),
    "Day": ("Trade Date", lambda df: df.groupby("Trade Date")),
    "Month": ("Trade Date", lambda df: df.groupby(df["Trade Date"].dt.to_period("M").astype(str).astype("category"))),
    "Year": ("Trade Date", lambda df: df.groupby(df["Trade Date"].dt.year.astype(int))),
}

AGGREGATIONS = {
    "Total": lambda df_gb: df_gb["Value"].apply(lambda x: np.abs(x).sum()),
    "Average": lambda df_gb: df_gb["Value"].apply(lambda x: np.abs(x).mean()),
    "Count": lambda df_gb: df_gb.size(),
}

def get_groupby() -> str:
    return st.selectbox("Group By", GROUPBY_OPTIONS_DICT.keys())

def get_aggregation() -> str:
    return st.selectbox("Aggregation Type", list(AGGREGATIONS.keys()), index=0)

def extract_gb_and_agg() -> Tuple[str, str]:
    st.write("### Trade Trends & Insights")
    gb_col, agg_col = st.columns(2)
    with gb_col:
        groupby = get_groupby()
    with agg_col:
        aggregation = get_aggregation()
    return groupby, aggregation

def apply_gb_and_agg(
    groupby: str,
    aggregation: str,
    dataset: pd.DataFrame
) -> pd.DataFrame:
    if aggregation not in AGGREGATIONS:
        raise ValueError(f"{aggregation}: Invalid value for aggregation; choose from {list(AGGREGATIONS.keys())}")
    df_plot: pd.DataFrame = GROUPBY_OPTIONS_DICT[groupby][1](dataset)
    df_plot: pd.Series = AGGREGATIONS[aggregation](df_plot).reset_index()
    df_plot.columns = [df_plot.columns[0], aggregation]
    x = GROUPBY_OPTIONS_DICT[groupby][0]
    return df_plot, x
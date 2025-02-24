from typing import Tuple
import streamlit as st
import pandas as pd
import numpy as np


# class GroupbyAndAggInputFields:

#     GROUPBY_OPTIONS_DICT = {
#         "Company": ("Company Name", lambda df: df.groupby("Company Name")),
#         "Day": ("Filing Date", lambda df: df.groupby(df["Filing Date"].dt.strftime("%Y-%m-%d"))),
#         "Month": ("Filing Date", lambda df: df.groupby(df["Filing Date"].dt.to_period("M").astype(str).astype("category"))),
#         # "Year": ("Filing Date", lambda df: df.groupby(df["Filing Date"].dt.year.astype(int))),
#     }
    
#     def get_gb_and_agg(self) -> Tuple[str, str]:
#         st.write("#### Group and Aggregate Data")
#         gb_col, agg_col = st.columns(2)
#         with gb_col:
#             groupby = self.get_groupby()
#         with agg_col:
#             aggregation = self.get_aggregation()
#         return groupby, aggregation

#     @classmethod
#     def get_groupby(cls) -> str:
#         return st.selectbox("Group By", cls.GROUPBY_OPTIONS_DICT.keys())

#     @staticmethod
#     def get_aggregation() -> str:
#         return st.selectbox("Aggregation Type", ["Count", "Total"], index=0)


GROUPBY_OPTIONS_DICT = {
    "Company": ("Company Name", lambda df: df.groupby("Company Name")),
    "Day": ("Filing Date", lambda df: df.groupby(df["Filing Date"].dt.strftime("%Y-%m-%d"))),
    "Month": ("Filing Date", lambda df: df.groupby(df["Filing Date"].dt.to_period("M").astype(str).astype("category"))),
    # "Year": ("Filing Date", lambda df: df.groupby(df["Filing Date"].dt.year.astype(int))),
}

def get_groupby() -> str:
    return st.selectbox("Group By", GROUPBY_OPTIONS_DICT.keys())

def get_aggregation() -> str:
    return st.selectbox("Aggregation Type", ["Count", "Total"], index=0)

def extract_gb_and_agg() -> Tuple[str, str]:
    st.write("#### Group and Aggregate Data")
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
    x = GROUPBY_OPTIONS_DICT[groupby][0]
    df_plot: pd.DataFrame = GROUPBY_OPTIONS_DICT[groupby][1](dataset) if groupby else dataset
    size = df_plot.size()
    if aggregation == "Total":
        df_plot: pd.Series = df_plot["Value"].apply(lambda x: np.abs(x).sum())
    else:
        df_plot: pd.Series = size
    df_plot: pd.DataFrame = df_plot.reset_index()
    df_plot.columns = [df_plot.columns[0], aggregation]
    return df_plot, x
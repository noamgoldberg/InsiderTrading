from typing import Union
import streamlit as st
import numpy as np

from core.query_agent import QueryAgent

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
from streamlit_app.group_and_agg import extract_gb_and_agg, apply_gb_and_agg
from streamlit_app.plot import plot_trade_chart


# (0) Establish Parameters
max_rows = 5000
trade_val_step = 50000
trade_val_round = -9

# (1) Initialize QueryAgent
query_agent = QueryAgent(
    remember=2, # remember data from up to 2 recent queries
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
default_dataset = st.session_state["datasets"]["default"]

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

# (3) Display Title, Sidebar, & Filters
st.set_page_config(page_title="Insider Trading Visualizer", page_icon="📈")
st.title("OpenInsider Data Analysis")
selected_filters = display_and_extract_filters(
    default_dataset=default_dataset,
    trade_val_step=trade_val_step,
    trade_val_round=trade_val_round,
)

# (4) Apply Filters, Set Active Data & Parameters
apply_filters(
    query_agent=query_agent,
    selected_filters=selected_filters,
    max_rows=max_rows,
)

# (6) Extract & Apply Groupby & Aggregation
groupby, aggregation = extract_gb_and_agg()
df_plot, x = apply_gb_and_agg(
    groupby,
    aggregation,
    get_active_dataset()
)

# (7) Get Top N
top_n = None
if groupby == "Company":
    top_n = st.slider("Show Top # Companies", min_value=5, max_value=min(df_plot.shape[0], 100), value=25, step=5)

# (7) Plot chart
st.subheader(f"{aggregation} of Trades Grouped by {groupby}")
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
    y=aggregation,
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

# 3. bubble chart
# 4. clear filters button
# 5. filter sets (i.e. last 5 weeks)

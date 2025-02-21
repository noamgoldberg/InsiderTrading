from typing import Union, Dict, List
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

from core.query_agent import QueryAgent
from core.parameters.job_titles import JobTitlesParam
    

def display_active_filters(
    *,
    trade_types: str | List[str] | None,
    job_titles: str | List[str] | None,
    insiders: str | List[str] | None,
    companies: str | List[str] | None,
    trade_val_min: int | None,
    trade_val_max: int | None,
) -> Dict[str, str]:
    trade_val_range = "All" if trade_val_min is None and trade_val_max is None else \
                      f"{trade_val_min:,} to {trade_val_max:,}" if trade_val_min is not None and trade_val_max is not None else \
                      f"Min: {trade_val_min:,}" if trade_val_min is not None else \
                      f"Max: {trade_val_max:,}"
    
    with st.expander("View Current Filters"):
        st.info(f"""###### Filters Currently Applied
    - Trade Types: {', '.join(trade_types) if trade_types else 'All'}
    - Job Titles: {', '.join(job_titles) if job_titles else 'All'}
    - Insiders: {', '.join(insiders) if insiders else 'All'}
    - Companies: {', '.join(companies) if companies else 'All'}
    - Trade Value Range: {trade_val_range}""")

# (1) Initialize QueryAgent
max_rows = 5000
query_agent = QueryAgent(
    remember=2,
    max_rows=max_rows
)

# (2) Query Default Dataset
trade_types = None
job_titles = None
insiders = None
companies = None
trade_val_min = None
trade_val_max = None
num_results = max_rows
if st.session_state.get("data", {}).get("default", None) is None:
    st.session_state["data"] = {
        "default": query_agent.scrape(
            trade_types=trade_types,
            job_titles=job_titles,
            trade_val_min=None,
            trade_val_max=None,
            num_results=num_results,
        ),
        "filtered": None
    }
df = st.session_state["data"]["default"]

# (3) Display Title, Sidebar, & Filters
st.title("OpenInsider Data Analysis")
st.sidebar.header("Filters")

default_trade_types = ["P - Purchase", "S - Sale"]

all_trade_types = df['Trade Type'].unique()
# all_job_titles = df['Title'].explode().unique()
all_job_titles = list(JobTitlesParam.JOB_TITLE_MAP.keys())
all_insiders = df['Insider Name'].unique()
all_companies = df['Company Name'].unique()

selected_trade_types = st.sidebar.multiselect(
    "Select Trade Types",
    all_trade_types,
    default=[tt for tt in default_trade_types if tt in all_trade_types]
)
selected_job_titles = st.sidebar.multiselect("Select Job Titles", all_job_titles)
selected_insiders = st.sidebar.multiselect("Select Insiders", all_insiders)
selected_companies = st.sidebar.multiselect("Select Companies", all_companies)
step = 50000
selected_trade_val_min = st.sidebar.number_input("Min Trade Value", min_value=0, value=int(round(df['Value'].abs().min(), -9)), step=step)
selected_trade_val_max = st.sidebar.number_input("Max Trade Value", min_value=0, value=int(round(df['Value'].abs().max(), -9)), step=step)

# (4) Apply Filters
if st.sidebar.button("Apply Filters"):
    job_titles = selected_job_titles
    insiders = selected_insiders
    companies = selected_companies
    trade_val_min = selected_trade_val_min
    trade_val_max = selected_trade_val_max
    st.session_state["data"]["filtered"] = query_agent.scrape(
        trade_types=[tt.split(" - ")[0] for tt in selected_trade_types],
        job_titles=selected_job_titles,
        trade_val_min=trade_val_min,
        trade_val_max=trade_val_max,
        num_results=max_rows,
    )
    if st.session_state["data"]["filtered"] is not None:
        df = st.session_state["data"]["filtered"]
    if selected_companies:
        df = df[df['Company Name'].isin(selected_companies)]
    if selected_insiders:
        df = df[df['Insider Name'].isin(selected_insiders)]

# (5) Display Aggregation & Groupby Fields
st.write("#### Group and Aggregate Data")
agg_col, gb_col = st.columns(2)
with agg_col:
    aggregation_option = st.selectbox("Aggregation Type", ["Count", "Total"], index=0)
gb_options_dict = {
    "Company": ("Company Name", lambda df: df.groupby("Company Name")),
    "Day": ("Filing Date", lambda df: df.groupby(df["Filing Date"].dt.strftime("%Y-%m-%d"))),
    "Month": ("Filing Date", lambda df: df.groupby(df["Filing Date"].dt.to_period("M").astype(str).astype("category"))),
    # "Year": ("Filing Date", lambda df: df.groupby(df["Filing Date"].dt.year.astype(int))),
}
with gb_col:
    gb_selected = st.selectbox("Group By", gb_options_dict.keys())

# (6) Apply Aggregation & Groupby
x = gb_options_dict[gb_selected][0]
df_plot: pd.DataFrame = gb_options_dict[gb_selected][1](df._get_numeric_data()) if gb_selected else df
top_n = None
size = df_plot.size()
if gb_selected == "Company":
    top_n = st.slider("Show Top # Companies", min_value=5, max_value=min(size.shape[0], 100), value=25, step=5)
if aggregation_option == "Total":
    df_plot: pd.Series = df_plot.sum().iloc[:, 0]
else:
    df_plot: pd.Series = size
df_plot: pd.DataFrame = df_plot.reset_index()
df_plot.columns = [df_plot.columns[0], aggregation_option]

# (7) Plot chart
st.subheader(f"{aggregation_option} of Trades Grouped by {gb_selected}")
display_active_filters(
    trade_types=trade_types,
    job_titles=job_titles,
    insiders=insiders,
    companies=companies,
    trade_val_min=trade_val_min,
    trade_val_max=trade_val_max,
)
temporal_gbs = ["Year", "Month", "Day"]
# if gb_selected in ["Year", "Day"]:
# # if gb_selected in ["Year", "Month"]:
#     df_plot.sort_values(by=x)
#     fig = px.line(
#         df_plot,
#         x=x,
#         y=aggregation_option,
#         title=f"{aggregation_option} of Trades Over Time",
#         labels={x: gb_selected, aggregation_option: aggregation_option},
#     )
if gb_selected in temporal_gbs:
    df_plot.sort_values(by=x, inplace=True)
    if gb_selected == "Month":
        df_plot[x] = df_plot[x].astype(str)  # Ensure categorical ordering
        fig = px.bar(
            df_plot,
            x=x,
            y=aggregation_option,
            title=f"{aggregation_option} of Trades Over Time",
            labels={x: gb_selected, aggregation_option: aggregation_option},
        )
        fig.update_xaxes(
            type="category"  # Prevents unnecessary intermediate months
        )
    else:
        fig = px.line(
            df_plot,
            x=x,
            y=aggregation_option,
            title=f"{aggregation_option} of Trades Over Time",
            labels={x: gb_selected, aggregation_option: aggregation_option},
        )
else:
    if top_n:
        df_plot = df_plot.head(top_n)
    orientation = "v"
    if gb_selected not in ["Year"]:
        orientation = 'h'
    fig = px.bar(
        df_plot.sort_values(by=aggregation_option, ascending=True),
        x=aggregation_option,
        y=x,
        title=f"{aggregation_option} of Trades by {gb_selected} (Top {top_n})",
        labels={x: gb_selected, aggregation_option: aggregation_option},
        orientation=orientation,
    )
    chart_height = max(400, 40 + df_plot.shape[0] * 20)
    fig.update_layout(
        height=chart_height
    )
st.plotly_chart(fig)
df_display = df.copy()
def format_dollar_amt(amt: Union[int, float], decimals: int = 2) -> str:
    sym = '-' if amt < 0 else ''
    return f"{sym}${abs(amt):,.{decimals}f}"
# df_display["Owned"] = df_display["Owned"].apply(lambda amt: format_dollar_amt(amt, 0) if amt else None)
df_display["Price"] = df_display["Price"].apply(lambda amt: format_dollar_amt(amt, 2) if amt not in [np.nan, None] else None)
df_display["Value"] = df_display["Value"].apply(lambda amt: format_dollar_amt(amt, 0) if amt not in [np.nan, None] else None)
df_display["ΔOwn"] = df_display["ΔOwn"].apply(lambda pct: f"{pct:.0%}" if pct not in [np.nan, None] else None)
st.write(df_display)
st.markdown(
    """
    <hr>
    <p style="font-size: 10px;">
    <strong>Filing Type:</strong><br>
    <strong>- A</strong> - Amended filing<br>
    <strong>- D</strong> - Derivative transaction in filing (usually option exercise)<br>
    <strong>- E</strong> - Error detected in filing<br>
    <strong>- M</strong> - Multiple transactions in filing; earliest reported transaction date and weighted average transaction price<br>
    <br>
    <strong>Trade Type</strong><br>
    <strong>- S - Sale</strong> - Sale of securities on an exchange or to another person<br>
    <strong>- S - Sale+OE</strong> - Sale of securities on an exchange or to another person (after option exercise)<br>
    <strong>- F - Tax</strong> - Payment of exercise price or tax liability using portion of securities received from the company<br>
    <strong>- P - Purchase</strong> - Purchase of securities on an exchange or from another person<br>
    </p>
    """,
    unsafe_allow_html=True
)
from typing import Dict, List, Any
import streamlit as st
import pandas as pd

from open_insider.parameters.job_titles import JobTitlesParam
from open_insider.query_agent import QueryAgent

from streamlit_app.active import set_active_dataset_and_params


def display_and_extract_filters(
    default_dataset: pd.DataFrame,
    trade_val_step: int = 50000,
    trade_val_round: int = -9
) -> Dict[str, Any]:
    st.sidebar.header("Filters")
    all_trade_types = default_dataset['Trade Type'].unique()
    all_job_titles = list(JobTitlesParam.JOB_TITLE_MAP.keys())
    all_insiders = default_dataset['Insider Name'].unique()
    all_companies = default_dataset['Company Name'].unique()

    default_trade_types = ["P - Purchase", "S - Sale"]
    selected_trade_types = st.sidebar.multiselect(
        "Select Trade Types",
        all_trade_types,
        default=[tt for tt in default_trade_types if tt in all_trade_types]
    )
    selected_job_titles = st.sidebar.multiselect("Select Job Titles", all_job_titles)
    selected_insiders = st.sidebar.multiselect("Select Insiders", all_insiders)
    selected_companies = st.sidebar.multiselect("Select Companies", all_companies)
    selected_trade_val_min = st.sidebar.number_input(
        "Min Trade Value",
        min_value=0,
        value=int(round(default_dataset['Value'].abs().min(), trade_val_round)),
        step=trade_val_step
    )
    selected_trade_val_max = st.sidebar.number_input(
        "Max Trade Value",
        min_value=0,
        value=int(round(default_dataset['Value'].abs().max(), trade_val_round)),
        step=trade_val_step
    )
    return {
        "trade_types": selected_trade_types,
        "job_titles": selected_job_titles,
        "insiders": selected_insiders,
        "companies": selected_companies,
        "trade_val_min": selected_trade_val_min,
        "trade_val_max": selected_trade_val_max,
    }

def apply_filters(
    *,
    query_agent: QueryAgent,
    selected_filters: Dict[str, Any],
    max_rows: int = 5000
) -> None:
    if st.sidebar.button("Apply Filters"):
        if st.session_state["active"]["params"] == selected_filters:
            set_active_dataset_and_params(
                dataset_name="default",
                params=selected_filters,
            )
        else:
            if st.session_state["active"]["params"] != selected_filters:
                df = query_agent.scrape(
                    trade_types=[tt.split(" - ")[0] for tt in selected_filters["trade_types"]],
                    job_titles=selected_filters["job_titles"],
                    trade_val_min=selected_filters["trade_val_min"],
                    trade_val_max=selected_filters["trade_val_max"],
                    num_results=max_rows,
                )
                if df.empty:
                    st.error("Failed to load data from OpenInsider.")
                else:
                    if selected_filters["companies"]:
                        df = df[df['Company Name'].isin(selected_filters["companies"])]
                    if selected_filters["insiders"]:
                        df = df[df['Insider Name'].isin(selected_filters["insiders"])]
                    st.session_state["datasets"]["filtered"] = df
                    set_active_dataset_and_params(
                        dataset_name="filtered",
                        params=selected_filters,
                    )


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


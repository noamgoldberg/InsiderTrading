from typing import Dict, Any
import pandas as pd
import streamlit as st


def set_active_dataset_and_params(
    *,
    dataset_name: str,
    params: Dict[str, Any],
) -> None:
    st.session_state["active"] = {
        "dataset": dataset_name,
        "params": params,
    }

def get_active_dataset() -> pd.DataFrame | None:
    dataset_name = st.session_state["active"]["dataset"]
    return st.session_state["datasets"][dataset_name]

def get_active_params() -> Dict[str, Any] | None:
    return st.session_state["active"]["params"]




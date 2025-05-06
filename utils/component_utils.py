# utils/component_utils.py

import streamlit as st
import pandas as pd
import functools

CATEGORY_MAP = {
    1: "Hardware",
    2: "Software",
    3: "Personnel",
    4: "Maintenance",
    5: "Telecom",
    6: "Cybersecurity",
    7: "BC/DR"
}

def init_session_state_from_components(controller):
    df = pd.DataFrame(controller.components)

    if df.empty:
        return

    # Store full component table
    st.session_state.components_df = df

    # Total IT Spend
    st.session_state.it_spend = df["Spend"].sum()

    # Average Risk
    st.session_state.average_risk = df["Risk Score"].mean()

    # Revenue (if controller provides it, else default)
    st.session_state.revenue = getattr(controller, "revenue", 5_000_000)

    # Expenses by Category ID (mapped to name)
    expense_by_category = df.groupby("Category")["Spend"].sum().to_dict()
    st.session_state.expense_by_category = {
        cat_id: expense_by_category.get(CATEGORY_MAP[cat_id], 0)
        for cat_id in CATEGORY_MAP
    }

    # Default: 0% change over 3 years unless set
    if "expense_growth" not in st.session_state:
        st.session_state.expense_growth = {
            cat_id: [0.0, 0.0, 0.0] for cat_id in CATEGORY_MAP
        }

    # Future Forecast Table (optional, to be built per page)
    forecast_df = pd.DataFrame({
        "Year": [2024, 2025, 2026]
    })
    for cat_id, name in CATEGORY_MAP.items():
        base = st.session_state.expense_by_category[cat_id]
        growth = st.session_state.expense_growth[cat_id]
        forecast_df[name] = [
            base * (1 + growth[0]),
            base * (1 + growth[0]) * (1 + growth[1]),
            base * (1 + growth[0]) * (1 + growth[1]) * (1 + growth[2]),
        ]
    st.session_state.expense_forecast_df = forecast_df

def require_component_data(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if "controller" not in st.session_state:
            st.warning("⚠️ Please start with the Component Mapping page to set up your IT components.")
            st.stop()
        else:
            init_session_state_from_components(st.session_state.controller)
        return func(*args, **kwargs)
    return wrapper

from typing import List

def get_components_by_system(system_name: str, components: List[dict]):
    return [comp for comp in components if comp.get("System") == system_name]

def get_unique_systems(components: List[dict]):
    return sorted(set(comp.get("System") for comp in components if "System" in comp and comp["System"]))



    def set_components(self, components):
        self.components = components

# utils/component_utils.py

import pandas as pd
import streamlit as st

def init_session_state_from_components(controller):
    """
    Loads component data from the controller into session_state for cross-tab use.
    """
    df_components = pd.DataFrame(controller.components)

    if df_components.empty:
        return

    st.session_state.it_spend = df_components["Spend"].sum()
    st.session_state.average_risk = df_components["Risk Score"].mean()
    st.session_state.cyber_spend = df_components[df_components["Category"] == "Cybersecurity"]["Spend"].sum()
    st.session_state.component_count = len(df_components)
    st.session_state.components_df = df_components

import streamlit as st

def initialize_session():
    defaults = {
        "started": False,
        "user_id": None,
        "component_mapping": {},
        "assessment_answers": {},
        "risk_inputs": {},
        "financial_forecast": {},
        "cybersecurity_scores": {},
        "strategic_roadmap": {},
        "modules_done": {},
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

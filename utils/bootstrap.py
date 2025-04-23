# utils/bootstrap.py
import streamlit as st
from utils.ai_assist import ai_assist_overlay

def page_bootstrap(current_page="Overview"):
    # Smart context auto-pull
    context = {
        "current_page": current_page,
        "revenue": st.session_state.get("revenue"),
        "it_expense": st.session_state.get("it_expense"),
        "components_loaded": len(st.session_state.controller.components) if "controller" in st.session_state else 0,
        "revenue_growth": st.session_state.get("revenue_growth"),
        "expense_growth": st.session_state.get("expense_growth"),
    }

    with st.sidebar.expander("💬 AI Assistant", expanded=False):
        ai_assist_overlay(context)

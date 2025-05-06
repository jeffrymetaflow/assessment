# utils/bootstrap.py
import streamlit as st
from utils.ai_assist import handle_ai_consultation


def ai_assist_overlay(user_prompt, session_state, role="CIO", goal="Optimize Costs"):
    return handle_ai_consultation(user_prompt, session_state, role, goal)

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
        user_prompt = st.text_input("Ask the AI Assistant:")
        if st.button("Submit"):
            response = ai_assist_overlay(
                user_prompt=user_prompt,
                session_state=st.session_state,
                role="CIO",
                goal="Optimize Costs"
            )
            st.text_area("AI Response:", response)


# utils/ai_assistant.py

import streamlit as st
from utils.intent_classifier import classify_intent

def ai_assist_overlay():
    st.markdown("### 🤖 Need help getting started?")
    prompt = st.text_input("Ask me about your IT plan", key="ai_prompt_input")

    if st.button("Ask AI", key="ai_button"):
        action = classify_intent(prompt)

        if action == "adjust_category_forecast":
            st.success("Adjusting forecast...")
        elif action == "report_summary":
            st.success("Generating IT spend report...")
        else:
            st.info("I'm still learning. Try asking about spend, margin, or categories.")

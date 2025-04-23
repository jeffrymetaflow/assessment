import streamlit as st
import openai
import os
from utils.intent_classifier import classify_intent
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search.tool import TavilySearchResults

# --- Overlay Entry Point ---
def ai_assist_overlay(context=None):
    try:
        openai_key = st.secrets["openai_api_key"]
        tavily_key = st.secrets["tavily_api_key"]
    except KeyError as e:
        st.error(f"Missing secret key: {e}")
        return

    os.environ["TAVILY_API_KEY"] = tavily_key
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=openai_key)
    search_tool = TavilySearchResults()
    agent = initialize_agent(
        tools=[search_tool],
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False,
        handle_parsing_errors=True
    )

    st.markdown("### 🤖 Ask Me Anything")

    # Context awareness display
    if context:
        st.info("**Context:** " + ", ".join([f"{k}: {v}" for k, v in context.items() if v]))

    user_prompt = st.text_input("What's your question or command?", key="ai_input")

    if st.button("Submit", key="ai_submit") and user_prompt:
        action = classify_intent(user_prompt)

        # Simple real-time adjustments (example)
        if "increase cybersecurity" in user_prompt.lower():
            st.session_state["Cybersecurity"] = st.session_state.get("Cybersecurity", 200000) * 1.10
            st.success("🔒 Cybersecurity budget increased by 10%.")
            return

        try:
            response = agent.run(user_prompt)
            st.success(response)
        except Exception as e:
            st.error(f"AI Error: {e}")

    # User journaling
    st.markdown("### 📝 Notes & Takeaways")
    notes = st.text_area("What do you want to remember?", key="journal_notes")
    if st.button("💾 Save Note"):
        st.session_state.setdefault("journal_log", []).append(notes)
        st.success("Note saved.")

    if "journal_log" in st.session_state:
        st.markdown("### 🗂️ Past Notes")
        for i, note in enumerate(st.session_state.journal_log[::-1]):
            st.markdown(f"**{len(st.session_state.journal_log)-i}.** {note}")

    # Real-time control input
    st.markdown("### ⚙️ Adjust IT Category Spend")
    category = st.selectbox("Category to adjust", ["Cybersecurity", "BC/DR", "Hardware", "Personnel", "Software", "Telecom"], key="cat_select")
    adjustment = st.slider("Adjustment (%)", -50, 50, 10, key="adjustment_slider")
    if st.button("🔧 Apply Adjustment", key="adjust_apply"):
        current_val = st.session_state.get(category, 100000)
        st.session_state[category] = current_val * (1 + adjustment / 100)
        st.success(f"{category} adjusted by {adjustment}% → ${st.session_state[category]:,.0f}")


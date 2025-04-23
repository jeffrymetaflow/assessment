import streamlit as st
import openai
import os
from utils.intent_classifier import classify_intent
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search.tool import TavilySearchResults
import matplotlib.pyplot as plt

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

    st.session_state.setdefault("conversation_history", [])

    user_prompt = st.text_input("What's your question or command?", key="ai_input")

    if st.button("Submit", key="ai_submit") and user_prompt:
        action = classify_intent(user_prompt)

        if "increase cybersecurity" in user_prompt.lower():
            st.session_state["Cybersecurity"] = st.session_state.get("Cybersecurity", 200000) * 1.10
            st.success("🔒 Cybersecurity budget increased by 10%.")
            return

        try:
            context_prefix = (
    "You are a strategic assistant for an IT Revenue Management (ITRM) platform. "
    "Your job is to guide users through budgeting decisions, category forecasting, IT-to-revenue ratio analysis, "
    "and strategic optimization across Cybersecurity, BC/DR, Hardware, Software, and Personnel. "
    "Do not answer like a personal finance assistant. Focus on enterprise-level IT planning."
)

            response = agent.run(f"""{context_prefix}

{user_prompt}""")
            st.session_state.conversation_history.append({"user": user_prompt, "ai": response})
            st.success(response)
        except Exception as e:
            st.error(f"AI Error: {e}")

    # --- Grouping remainder in a main container (avoids nested expander issues) ---
    with st.container():

        # Conversation History (Flat Display - avoids nested expanders)
        if st.session_state.conversation_history:
            st.markdown("### 🧾 Conversation History")
            for turn in st.session_state.conversation_history:
                st.markdown(f"**You:** {turn['user']}")
                if "ai" in turn:
                    st.markdown(f"**AI:** {turn['ai']}")

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

        # Strategic Summary Generation
        if st.button("🧠 Summarize My Strategy", key="summarize_btn"):
            summary_prompt = f"""
            Provide a concise strategic recommendation summary based on:
            - Revenue: {st.session_state.get('revenue')}
            - IT Expense: {st.session_state.get('it_expense')}
            - Cybersecurity Spend: {st.session_state.get('Cybersecurity')}
            - BC/DR: {st.session_state.get('BC/DR')}
            - Growth Rates: {st.session_state.get('revenue_growth')} / {st.session_state.get('expense_growth')}
            """
            try:
                summary = agent.run(summary_prompt)
                st.success(summary)
            except Exception as e:
                st.error(f"AI Summary Error: {e}")

        # Scenario Simulation
        st.markdown("### 🔮 Simulate Future Scenario")
        sim_category = st.selectbox("Which category would you like to simulate?", ["Cybersecurity", "BC/DR", "Hardware", "Personnel", "Software", "Telecom"], key="sim_category")
        sim_growth = st.slider("Growth Impact (%)", -50, 100, 15, step=5, key="sim_growth")
        sim_years = st.slider("Years to Project", 1, 5, 3, key="sim_years")

        if st.button("📈 Run Simulation", key="run_simulation"):
            base_val = st.session_state.get(sim_category, 100000)
            projected = [base_val * ((1 + sim_growth / 100) ** year) for year in range(sim_years)]
            result_str = "\n".join([f"Year {i+1}: ${val:,.0f}" for i, val in enumerate(projected)])
            st.success(f"Projected {sim_category} Spend over {sim_years} years with {sim_growth}% growth:\n\n{result_str}")

            # Chart visualization
            st.markdown("### 📊 Simulation Chart")
            fig, ax = plt.subplots()
            ax.plot([f"Year {i+1}" for i in range(sim_years)], projected, marker='o')
            ax.set_title(f"{sim_category} Spend Simulation")
            ax.set_ylabel("Spend ($)")
            ax.set_xlabel("Year")
            st.pyplot(fig)

        # Prompt suggestions
        st.markdown("### 💡 Suggested Prompts:")
        st.markdown("- What’s my IT-to-Revenue ratio?")
        st.markdown("- Where am I overspending?")
        st.markdown("- Suggest categories to consolidate")
        st.markdown("- Simulate what happens if BC/DR grows 30% over 3 years")

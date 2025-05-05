import streamlit as st
import openai
import os
import pandas as pd
import matplotlib.pyplot as plt
from utils.intent_classifier import classify_intent
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from langchain_core.callbacks.manager import CallbackManagerForToolRun
from utils.session_state import initialize_session
initialize_session()
from utils.auth import enforce_login
enforce_login()

st.set_page_config(page_title="ITRM AI Assistant", layout="wide")
st.title("\U0001F916 ITRM Conversational AI Assistant")

# --- Load API Keys with Fallback ---
try:
    openai_key = st.secrets["openai_api_key"]
    tavily_key = st.secrets["tavily_api_key"]
except KeyError as e:
    st.error(f"Missing secret key: {e}")
    st.stop()

# --- Set environment variable for Tavily ---
os.environ["TAVILY_API_KEY"] = tavily_key

# --- Initialize LangChain Web Agent ---
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=openai_key)
search_tool = TavilySearchResults()
agent = initialize_agent(
    tools=[search_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,
    handle_parsing_errors=True
)

def query_langchain_product_agent(prompt):
    try:
        return agent.run(prompt)
    except Exception as e:
        return f"Error fetching product info: {str(e)}"

# --- Placeholder Simulated State (would be tied to real modules later) ---
session_state = {
    "Hardware": 320000,
    "Software": 280000,
    "Personnel": 500000,
    "Maintenance": 160000,
    "Telecom": 120000,
    "Cybersecurity": 220000,
    "BC/DR": 140000,
    "Revenue": 100_000_000
}

# --- Sidebar Context Awareness ---
st.sidebar.subheader("\U0001F464 Consultant Context")
user_role = st.sidebar.selectbox("Your Role", ["CIO", "IT Ops", "Finance Lead", "Security Officer"])
user_goal = st.sidebar.selectbox("Primary Goal", ["Optimize Costs", "Improve Resilience", "Modernize IT", "Enhance Security"])

def contextualize(prompt):
    return f"You are advising a {user_role} focused on {user_goal}. {prompt}"

# --- Sample Simulated Actions ---
def adjust_category_forecast(prompt):
    for cat in session_state:
        if cat.lower() in prompt.lower():
            if "increase" in prompt:
                session_state[cat] *= 1.10
                return f"Increased {cat} budget by 10%. New value: ${session_state[cat]:,.0f}"
            elif "decrease" in prompt:
                session_state[cat] *= 0.90
                return f"Decreased {cat} budget by 10%. New value: ${session_state[cat]:,.0f}"
    return "Which category would you like to adjust?"

def report_summary(prompt):
    total_spend = sum([v for k, v in session_state.items() if k != "Revenue"])
    ratio = total_spend / session_state["Revenue"] * 100
    return f"Total IT Spend: ${total_spend:,.0f}\nIT-to-Revenue Ratio: {ratio:.2f}%"

def recommend_action(prompt):
    return "You could reduce Telecom and Maintenance by 15% to save money without significantly increasing risk."

def show_risk_insight(prompt):
    return "Cybersecurity and BC/DR protect 43% of revenue with a combined ROPR of 5.3x."

def optimize_margin(prompt):
    return "To improve margin by 2%, consider reducing Personnel and Maintenance by 5% each."

def architecture_gap_analysis(prompt):
    return "Compared to hybrid cloud best practices, you may have an over-concentration in on-prem hardware with limited containerization or automation."

def tool_roi_justification(prompt):
    return "Switching to Rubrik from Commvault could reduce backup windows by 40% and lower TCO by 15% over 3 years."

# --- Extend classifier fallback logic ---
def fallback_classifier(prompt):
    fallback_keywords = ["compare", "alternative", "better than", "replace", "options", "suggest"]
    for keyword in fallback_keywords:
        if keyword in prompt.lower():
            return "analyze_product"
    if "roi" in prompt.lower() or "value of" in prompt.lower():
        return "tool_roi"
    if "architecture gap" in prompt.lower() or "best practice" in prompt.lower():
        return "arch_gap"
    return "unknown"

# --- Prompt Input ---
st.subheader("\U0001F4AC Ask me anything about your IT strategy")
user_prompt = st.text_input("Type your question or command:", "What is my current IT spend?")

if st.button("Submit"):
    action = classify_intent(user_prompt)
    if action == "unknown":
        action = fallback_classifier(user_prompt)

    full_prompt = contextualize(user_prompt)

    if action == "adjust_category_forecast":
        response = adjust_category_forecast(user_prompt)
    elif action == "report_summary":
        response = report_summary(user_prompt)
    elif action == "recommend_action":
        response = recommend_action(user_prompt)
    elif action == "show_risk_insight":
        response = show_risk_insight(user_prompt)
    elif action == "optimize_margin":
        response = optimize_margin(user_prompt)
    elif action == "analyze_product":
        raw_response = query_langchain_product_agent(full_prompt)
        if "Dell" in raw_response and "NetApp" in raw_response:
            st.markdown("### Product Comparison Table")
            st.table({
                "Feature": ["Focus", "Top Product", "Performance", "Pricing", "Gartner Rating"],
                "NetApp": [
                    "Data infrastructure & cloud",
                    "AFF series",
                    "Exceptional speed, cutting-edge flash",
                    "Higher cost",
                    "Slightly higher"
                ],
                "Dell EMC": [
                    "PCs, servers, storage",
                    "PowerMax",
                    "Ultra-low latency, high IOPS",
                    "More competitive",
                    "Slightly lower"
                ]
            })
        response = raw_response + "\n\nFeel free to ask: 'Which is better for hybrid workloads?' or 'Compare with Pure Storage'"
    elif action == "tool_roi":
        response = tool_roi_justification(full_prompt)
    elif action == "arch_gap":
        response = architecture_gap_analysis(full_prompt)
    else:
        response = "I'm not sure how to help with that yet. Try asking about your budget, risk, or tools."

    st.success(response)

    # --- Visual Summary Chart ---
    st.subheader("\U0001F4CA Budget Overview Chart")
    df = pd.DataFrame({
        "Category": [k for k in session_state if k != "Revenue"],
        "Spend": [v for k, v in session_state.items() if k != "Revenue"]
    })
    df = df.sort_values("Spend", ascending=False)

    fig, ax = plt.subplots()
    ax.barh(df["Category"], df["Spend"], color="skyblue")
    ax.set_xlabel("Spend ($)")
    ax.set_title("IT Budget Allocation by Category")
    st.pyplot(fig)

# --- Debug Info (optional) ---
with st.expander("\U0001F527 Simulated Data State"):
    st.write(session_state)

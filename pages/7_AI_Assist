import streamlit as st
import openai
import os
from intent_classifier import classify_intent
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from langchain_core.callbacks.manager import CallbackManagerForToolRun

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

# --- Extend classifier fallback logic ---
def fallback_classifier(prompt):
    fallback_keywords = ["compare", "alternative", "better than", "replace", "options", "suggest"]
    for keyword in fallback_keywords:
        if keyword in prompt.lower():
            return "analyze_product"
    return "unknown"

# --- Prompt Input ---
st.subheader("\U0001F4AC Ask me anything about your IT strategy")
user_prompt = st.text_input("Type your question or command:", "What is my current IT spend?")

if st.button("Submit"):
    action = classify_intent(user_prompt)
    if action == "unknown":
        action = fallback_classifier(user_prompt)

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
        raw_response = query_langchain_product_agent(user_prompt)
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
    
        st.success(response)

# --- Debug Info (optional) ---
with st.expander("\U0001F527 Simulated Data State"):
    st.write(session_state)

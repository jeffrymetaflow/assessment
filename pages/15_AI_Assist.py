import streamlit as st
import openai
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import hashlib
from utils.intent_classifier import classify_intent
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from langchain_core.callbacks.manager import CallbackManagerForToolRun
from utils.session_state import initialize_session
initialize_session()
from utils.auth import enforce_login
enforce_login()
from utils.vector_index import answer_with_code_context, preview_indexed_docs

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

# 🔍 Enhanced tool for app logic awareness using live module summaries
def fetch_module_summary(prompt: str, run_manager: CallbackManagerForToolRun = None):
    components = st.session_state.get("components", [])
    if not components:
        return "No component data found to analyze."

    df = pd.DataFrame(components)
    summary = []
    summary.append(f"You have {len(df)} components across {df['Category'].nunique()} categories.")
    summary.append("Top categories by spend:")
    top = df.groupby("Category")["Spend"].sum().sort_values(ascending=False).head(5)
    for cat, val in top.items():
        summary.append(f"- {cat}: ${val:,.0f}")
    return "\n".join(summary)

from langchain.tools import Tool
module_summary_tool = Tool(
    name="AppModuleSummary",
    func=fetch_module_summary,
    description="Provides insight into the internal application module architecture and logic."
)

agent = initialize_agent(
    tools=[search_tool, module_summary_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,
    handle_parsing_errors=True
)

# --- Remaining logic unchanged below ---

def query_langchain_product_agent(prompt):
    try:
        return agent.run(prompt)
    except Exception as e:
        return f"Error fetching product info: {str(e)}"

if "revenue" not in st.session_state:
    st.warning("Revenue not found in session state. Please complete the project setup on the main page.")
    st.stop()

categories = ["Hardware", "Software", "Personnel", "Maintenance", "Telecom", "Cybersecurity", "BC/DR"]

session_state = {cat: 0 for cat in categories}
for component in st.session_state.get("components", []):
    cat = component.get("Category")
    spend = component.get("Spend", 0)
    if cat in session_state:
        session_state[cat] += spend
session_state["Revenue"] = st.session_state.get("revenue", 100_000_000)

st.sidebar.subheader("\U0001F464 Consultant Context")
user_role = st.sidebar.selectbox("Your Role", ["CIO", "IT Ops", "Finance Lead", "Security Officer"])
user_goal = st.sidebar.selectbox("Primary Goal", ["Optimize Costs", "Improve Resilience", "Modernize IT", "Enhance Security"])

def contextualize(prompt):
    return f"You are advising a {user_role} focused on {user_goal}. {prompt}"

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

def fallback_classifier(prompt):
    prompt_lower = prompt.lower()
    if any(k in prompt_lower for k in ["compare", "alternative", "better than", "replace", "options", "suggest"]):
        return "analyze_product"
    elif any(k in prompt_lower for k in ["roi", "value of", "justification", "return on investment"]):
        return "tool_roi"
    elif any(k in prompt_lower for k in ["architecture", "best practice", "design gap", "blueprint"]):
        return "arch_gap"
    elif any(k in prompt_lower for k in ["it spend", "how much", "summary", "ratio"]):
        return "report_summary"
    elif any(k in prompt_lower for k in ["cut", "reduce", "increase", "adjust", "budget change"]):
        return "adjust_category_forecast"
    elif any(k in prompt_lower for k in ["risk", "vulnerability", "protection"]):
        return "show_risk_insight"
    elif any(k in prompt_lower for k in ["margin", "profit", "efficiency"]):
        return "optimize_margin"
    return "unknown"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.subheader("\U0001F4AC Ask your Smart IT Consultant")
with st.form("chat_form"):
    user_prompt = st.text_input("Your question or command:", "What is my current IT spend?")
    submitted = st.form_submit_button("Ask")

if submitted:
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
        response = query_langchain_product_agent(full_prompt)
    elif action == "tool_roi":
        response = tool_roi_justification(full_prompt)
    elif action == "arch_gap":
        response = architecture_gap_analysis(full_prompt)
    else:
        response = "I'm not sure how to help with that yet. Try asking about your budget, risk, or tools."

    st.session_state.chat_history.append((user_prompt, response))

for i, (user, bot) in enumerate(reversed(st.session_state.chat_history)):
    st.markdown(f"**You:** {user}")
    st.markdown(f"**Consultant:** {bot}")
    st.markdown("---")

if st.session_state.chat_history:
    st.subheader("\U0001F4CA Budget Overview Heatmap")
    df = pd.DataFrame({
        "Category": [k for k in session_state if k != "Revenue"],
        "Spend": [v for k, v in session_state.items() if k != "Revenue"]
    }).sort_values("Spend", ascending=False)

    df["IT/Revenue %"] = df["Spend"] / session_state["Revenue"] * 100
    df.set_index("Category", inplace=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(df[["Spend"]], annot=True, fmt=".0f", cmap="YlGnBu", linewidths=0.5, ax=ax)
    ax.set_title("Category-Level IT Spend Heatmap")
    st.pyplot(fig)

    st.subheader("\U0001F4C8 IT-to-Revenue Ratio by Category")
    fig2, ax2 = plt.subplots()
    df["IT/Revenue %"].plot(kind="bar", color="skyblue", ax=ax2)
    ax2.axhline(y=df["IT/Revenue %"].mean(), color='red', linestyle='--', label=f"Average: {df['IT/Revenue %'].mean():.2f}%")
    ax2.set_ylabel("% of Revenue")
    ax2.set_title("Spending Efficiency per Category")
    ax2.legend()
    st.pyplot(fig2)

with st.expander("\U0001F527 Session Data Snapshot"):
    st.write(session_state)

st.subheader("🧠 Ask About App Logic or Architecture")

code_query = st.text_input("Ask something about how the app works (e.g., 'How is risk calculated?')")

if st.button("Ask App Logic AI"):
    if code_query:
        response = answer_with_code_context(code_query)
        st.markdown(f"**Consultant (with code context):** {response}")
    else:
        st.warning("Please enter a question.")

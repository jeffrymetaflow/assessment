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

st.sidebar.subheader("\U0001F464 Consultant Context")
user_role = st.sidebar.selectbox("Your Role", ["CIO", "IT Ops", "Finance Lead", "Security Officer"])
user_goal = st.sidebar.selectbox("Primary Goal", ["Optimize Costs", "Improve Resilience", "Modernize IT", "Enhance Security"])

def contextualize(prompt):
    return f"You are advising a {user_role} focused on {user_goal}. {prompt}"

def recommend_action(prompt):
    return "You could reduce Telecom and Maintenance by 15% to save money without significantly increasing risk."

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

def generate_maturity_recommendation(category: str, question_summary: str = "") -> str:
    """
    Uses the AI assistant to generate improvement recommendations for a low-maturity category.
    """
    prompt = (
        f"The IT maturity category '{category}' scored low. "
        f"Recommend practical steps, tools, services, or best practices that could help an organization "
        f"improve in this area. {question_summary.strip() if question_summary else ''} "
        f"Focus on changes that could shift this maturity from 'low' to 'moderate' or 'high'."
    )
    response = llm.invoke(prompt)
    return response.content.strip()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.subheader("\U0001F4AC Ask your Smart IT Consultant")
with st.form("chat_form"):
    user_prompt = st.text_input("Your question or command:", "What is my current IT spend?")
    submitted = st.form_submit_button("Ask")

for i, (user, bot) in enumerate(reversed(st.session_state.chat_history)):
    st.markdown(f"**You:** {user}")
    st.markdown(f"**Consultant:** {bot}")
    st.markdown("---")

code_query = st.text_input("Ask something about how the app works (e.g., 'How is risk calculated?')")

if st.button("Ask App Logic AI"):
    if code_query:
        response = answer_with_code_context(code_query)
        st.markdown(f"**Consultant (with code context):** {response}")
    else:
        st.warning("Please enter a question.")


st.subheader("🧠 Ask for a Category-Specific AI Recommendation")
category_input = st.text_input("Enter a Cybersecurity or IT category (e.g., 'Identity', 'Endpoint Protection')")

if st.button("🔍 Generate Smart Recommendation") and category_input:
    with st.spinner(f"Analyzing maturity gap for '{category_input}'..."):
        result = generate_maturity_recommendation_with_products(category_input)

    st.success("✅ AI Recommendation Generated")
    st.markdown(f"**📂 Category:** `{category_input}`")
    st.markdown(f"**🔧 Recommendation:** {result.get('recommendation', 'N/A')}")
    st.markdown(f"**🛍️ Suggested Products/Services:** {', '.join(result.get('products', [])) or 'N/A'}")

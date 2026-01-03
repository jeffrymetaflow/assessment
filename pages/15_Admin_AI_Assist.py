import streamlit as st
import os
import openai
import pandas as pd
import re
from utils.intent_classifier import classify_intent
from utils.session_state import initialize_session
from utils.auth import enforce_login
from utils.vector_index import answer_with_code_context
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from langchain_core.callbacks.manager import CallbackManagerForToolRun

# --- Initialize ---
st.set_page_config(page_title="ITRM AI Assistant", layout="wide")
st.title("🤖 ITRM Conversational AI Assistant")
initialize_session()
enforce_login()

# --- API Key Setup ---
try:
    openai_key = st.secrets["openai_api_key"]
    tavily_key = st.secrets["tavily_api_key"]
except KeyError as e:
    st.error(f"Missing secret key: {e}")
    st.stop()

os.environ["TAVILY_API_KEY"] = tavily_key

# --- LLM and Search Agent ---
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=openai_key)
search_tool = TavilySearchResults()

# --- App module summarizer tool ---
def fetch_module_summary(prompt: str, run_manager: CallbackManagerForToolRun = None):
    components = st.session_state.get("components", [])
    if not components:
        return "No component data found to analyze."

    df = pd.DataFrame(components)
    summary = [f"You have {len(df)} components across {df['Category'].nunique()} categories."]
    top = df.groupby("Category")["Spend"].sum().sort_values(ascending=False).head(5)
    summary.append("Top categories by spend:")
    for cat, val in top.items():
        summary.append(f"- {cat}: ${val:,.0f}")
    return "\n".join(summary)

module_summary_tool = Tool(
    name="AppModuleSummary",
    func=fetch_module_summary,
    description="Provides insight into the internal application module architecture and logic."
)

# --- LangChain Agent ---
agent = initialize_agent(
    tools=[search_tool, module_summary_tool],
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

# --- Sidebar Context ---
st.sidebar.subheader("👤 Consultant Context")
user_role = st.sidebar.selectbox("Your Role", ["CIO", "IT Ops", "Finance Lead", "Security Officer"])
user_goal = st.sidebar.selectbox("Primary Goal", ["Optimize Costs", "Improve Resilience", "Modernize IT", "Enhance Security"])

def contextualize(prompt):
    return f"You are advising a {user_role} focused on {user_goal}. {prompt}"

# --- Chat Memory Setup ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Chat UI ---
st.subheader("💬 Ask your Smart IT Consultant")
with st.form("chat_form"):
    user_prompt = st.text_input("Your question or command:", "What is my current IT spend?")
    submitted = st.form_submit_button("Ask")
    if submitted and user_prompt:
        result = query_langchain_product_agent(contextualize(user_prompt))
        st.session_state.chat_history.append((user_prompt, result))

for user, bot in reversed(st.session_state.chat_history):
    st.markdown(f"**You:** {user}")
    st.markdown(f"**Consultant:** {bot}")
    st.markdown("---")

# --- Code Context Assistant ---
st.subheader("🧠 Ask App Logic AI")
code_query = st.text_input("Ask how something works inside the app (e.g., 'How is risk calculated?')")
if st.button("Ask App Logic AI"):
    if code_query:
        response = answer_with_code_context(code_query)
        st.markdown(f"**Consultant (with code context):** {response}")
    else:
        st.warning("Please enter a question.")

# --- Maturity Recommendation Generator ---
def generate_maturity_recommendation(category: str, question_summary: str = "") -> str:
    prompt = (
        f"The IT maturity category '{category}' scored low. "
        f"Recommend practical steps, tools, services, or best practices that could help an organization "
        f"improve in this area. {question_summary.strip() if question_summary else ''} "
        f"Focus on changes that could shift this maturity from 'low' to 'moderate' or 'high'."
    )
    response = llm.invoke(prompt)
    return response.content.strip()

st.subheader("📈 Generate Category-Specific Recommendation")
category_input = st.text_input("Enter a Cybersecurity or IT category (e.g., 'Identity', 'Endpoint Protection')")
if st.button("🔍 Generate Smart Recommendation") and category_input:
    with st.spinner(f"Analyzing maturity gap for '{category_input}'..."):
        raw = generate_maturity_recommendation(category_input)
    st.success("✅ AI Recommendation Generated")
    st.markdown(f"**📂 Category:** `{category_input}`")
    st.markdown(f"**🔧 Recommendation:** {raw}")

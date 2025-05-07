import openai
import os
import pandas as pd
import streamlit as st
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from langchain_core.callbacks.manager import CallbackManagerForToolRun
from langchain.tools import Tool
from utils.intent_classifier import classify_intent


# --- Load API Keys ---
openai_key = st.secrets["openai_api_key"]
tavily_key = st.secrets["tavily_api_key"]
os.environ["TAVILY_API_KEY"] = tavily_key or ""

# --- LangChain Agent ---
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=openai_key)
search_tool = TavilySearchResults()

def fetch_module_summary(prompt: str, run_manager: CallbackManagerForToolRun = None):
    import streamlit as st
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

agent = initialize_agent(
    tools=[search_tool, module_summary_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,
    handle_parsing_errors=True
)

def answer_with_code_context(query: str):
    if not openai_key:
        return "❌ OpenAI API key not configured."

    try:
        vectorstore = load_vector_index()
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        qa = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(temperature=0, api_key=st.secrets["openai_api_key"]),
            chain_type="stuff",
            retriever=retriever
        )
        return qa.run(query)
    except Exception as e:
        return f"❌ AI error: {e}"

# --- AI Logic Functions ---
def adjust_category_forecast(prompt, session_state):
    for cat in session_state:
        if cat.lower() in prompt.lower():
            if "increase" in prompt:
                session_state[cat] *= 1.10
                return f"Increased {cat} budget by 10%. New value: ${session_state[cat]:,.0f}"
            elif "decrease" in prompt:
                session_state[cat] *= 0.90
                return f"Decreased {cat} budget by 10%. New value: ${session_state[cat]:,.0f}"
    return "Which category would you like to adjust?"

def report_summary(prompt, session_state):
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

def query_langchain_product_agent(prompt):
    try:
        return agent.run(prompt)
    except Exception as e:
        return f"Error fetching product info: {str(e)}"

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

def generate_maturity_recommendation_with_products(category: str) -> dict:
    """
    Uses the AI assistant to generate both a recommendation and a product list for a low-maturity cybersecurity category.
    Returns a dictionary like: {"recommendation": "...", "products": ["Product1", "Product2"]}
    """
    prompt = (
        f"The cybersecurity category '{category}' scored low in a maturity assessment. "
        f"Suggest a practical improvement recommendation, and include a list of commercial tools or services "
        f"that would help an enterprise improve in this area.\n\n"
        f"Return your response in JSON format:\n"
        f"{{\"recommendation\": \"...\", \"products\": [\"...\", \"...\"]}}"
    )

    response = llm.invoke(prompt)

    # Parse and safely return the result
    try:
        import json
        return json.loads(response.content)
    except Exception:
        return {
            "recommendation": response.content.strip(),
            "products": []
        }

# --- Central AI Assist Dispatch Function ---
def handle_ai_consultation(user_prompt, session_state, role="CIO", goal="Optimize Costs"):
    intent = classify_intent(user_prompt)
    if intent == "unknown":
        intent = fallback_classifier(user_prompt)
    full_prompt = f"You are advising a {role} focused on {goal}. {user_prompt}"

    if intent == "adjust_category_forecast":
        return adjust_category_forecast(user_prompt, session_state)
    elif intent == "report_summary":
        return report_summary(user_prompt, session_state)
    elif intent == "recommend_action":
        return recommend_action(user_prompt)
    elif intent == "show_risk_insight":
        return show_risk_insight(user_prompt)
    elif intent == "optimize_margin":
        return optimize_margin(user_prompt)
    elif intent == "analyze_product":
        return query_langchain_product_agent(full_prompt)
    elif intent == "tool_roi":
        return tool_roi_justification(full_prompt)
    elif intent == "arch_gap":
        return architecture_gap_analysis(full_prompt)
    else:
        return "I'm not sure how to help with that yet. Try asking about your budget, risk, or tools."


    prompt = (
        f"The following text is from a company's 10-K filing:\n\n{excerpt}\n\n"
        f"What is the total annual revenue reported in this filing? Return only the dollar figure."
)

import openai
import os
import json
import pandas as pd
import streamlit as st
from datetime import datetime
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from langchain_core.callbacks.manager import CallbackManagerForToolRun
from langchain.tools import Tool
from utils.intent_classifier import classify_intent
from postgrest.exceptions import APIError
from utils.supabase_client import supabase
from tavily import TavilyClient

# --- Load API Keys ---
openai_key = st.secrets["openai_api_key"]
tavily_key = st.secrets["tavily_api_key"]
os.environ["TAVILY_API_KEY"] = tavily_key or ""

# --- LangChain Agent ---
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=openai_key)
search_tool = TavilySearchResults()

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
        from utils.vector_index import load_vector_index
        vectorstore = load_vector_index()
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        from langchain.chains import RetrievalQA
        qa = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(temperature=0, openai_api_key=openai_key),
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

def generate_it_maturity_recommendation_with_products(category: str) -> dict:
    return generate_ai_maturity_recommendation_with_products(category)

def generate_ai_maturity_recommendation_with_products(category: str) -> dict:
    try:
        response = supabase.table("ai_product_recommendations").select("*").eq("category", category).execute()
        if response.data:
            st.info(f"✅ Using cached recommendation for '{category}' from Supabase.")
            return {
                "recommendation": response.data[0]["recommendation"],
                "products": response.data[0]["products"]
            }

        dynamic_products = get_dynamic_product_recommendations(category)
        if not dynamic_products:
            return {
                "recommendation": f"No dynamic products found for {category}.",
                "products": []
            }

        recommendation = (
            f"These tools are well-suited for improving **{category}** maturity. "
            "Focus on high-suitability tools first."
        )

        supabase.table("ai_product_recommendations").insert({
            "category": category,
            "recommendation": recommendation,
            "products": dynamic_products,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        st.info(f"💡 New recommendation generated and cached for '{category}'.")
        return {"recommendation": recommendation, "products": dynamic_products}

    except APIError as e:
        st.warning(f"⚠️ Supabase error: {e}")
    except Exception as e:
        st.error(f"❌ Error generating recommendations: {e}")
    return {"recommendation": f"Failed to generate recommendations for {category}.", "products": []}

def get_dynamic_product_recommendations(category: str) -> list:
    try:
        tavily = TavilyClient(api_key=tavily_key)
        query = f"Top enterprise tools or platforms for improving {category} AI maturity"
        results = tavily.search(query, max_results=5)

        combined = " ".join([
            f"{r.get('title', '')} — {r.get('snippet', '')}" for r in results if isinstance(r, dict) and r.get("snippet")
        ])

        prompt = (
            f"Based on this content:\n{combined}\n\n"
            f"List 3-5 tools for '{category}' in AI maturity. Format as JSON:\n"
            "[{\"name\": \"\", \"features\": [\"\"], \"price_estimate\": \"\", \"suitability\": \"\"}]"
        )

        client = openai.OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        content = response.choices[0].message.content
        st.write(f"📦 Raw GPT Response for '{category}':\n", content)

        parsed = json.loads(content)
        return parsed if isinstance(parsed, list) else []

    except Exception as e:
        st.error(f"❌ Error in dynamic product fetch for '{category}': {e}")
        return []

def generate_cybersecurity_recommendation_with_products(category: str) -> dict:
    try:
        response = supabase.table("cyber_product_recommendations").select("*").eq("category", category).execute()
        if response.data:
            st.info(f"✅ Using cached cybersecurity recommendation for '{category}' from Supabase.")
            return {
                "recommendation": response.data[0]["recommendation"],
                "products": response.data[0]["products"]
            }

        query = f"Best enterprise cybersecurity tools for {category}"
        tavily = TavilyClient(api_key=tavily_key)
        results = tavily.search(query, max_results=5)

        combined = " ".join([
            f"{r.get('title', '')} — {r.get('snippet', '')}" for r in results if isinstance(r, dict) and r.get("snippet")
        ])

        prompt = (
            f"Based on this content:\n{combined}\n\n"
            f"List 3-5 cybersecurity tools for '{category}'. Format as JSON:\n"
            "[{\"name\": \"\", \"features\": [\"\"], \"price_estimate\": \"\", \"suitability\": \"\"}]"
        )

        client = openai.OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        content = response.choices[0].message.content
        st.write(f"📦 Raw Cybersecurity GPT Response for '{category}':\n", content)

        parsed = json.loads(content)
        if not parsed:
            return {"recommendation": f"No cybersecurity tools found for {category}.", "products": []}

        recommendation = (
            f"These cybersecurity tools align well with improving **{category}** maturity and risk posture."
        )

        supabase.table("cyber_product_recommendations").insert({
            "category": category,
            "recommendation": recommendation,
            "products": parsed,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        return {"recommendation": recommendation, "products": parsed}

    except Exception as e:
        st.error(f"❌ Cyber recommendation error for '{category}': {e}")
        return {"recommendation": f"Error retrieving cybersecurity products for {category}.", "products": []}

import os
import json
import pandas as pd
import streamlit as st
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

from utils.intent_classifier import classify_intent
from utils.supabase_client import supabase
from postgrest.exceptions import APIError
from tavily import TavilyClient

# ────────────────────────────────────────────────────────────────
# API Keys
# ────────────────────────────────────────────────────────────────
openai_key = st.secrets["openai_api_key"]
tavily_key = st.secrets["tavily_api_key"]
os.environ["TAVILY_API_KEY"] = tavily_key or ""

# ────────────────────────────────────────────────────────────────
# TOOL DEFINITIONS
# ────────────────────────────────────────────────────────────────
@tool
def app_module_summary() -> str:
    """Summarize application module architecture and spend."""
    components = st.session_state.get("components", [])
    if not components:
        return "No component data found."

    df = pd.DataFrame(components)
    summary = [f"{len(df)} components across {df['Category'].nunique()} categories."]
    top = df.groupby("Category")["Spend"].sum().sort_values(ascending=False).head(5)

    for cat, val in top.items():
        summary.append(f"{cat}: ${val:,.0f}")

    return "\n".join(summary)

search_tool = TavilySearchResults()

TOOLS = [search_tool, app_module_summary]

# ────────────────────────────────────────────────────────────────
# Cached LLM with tools bound
# ────────────────────────────────────────────────────────────────
@st.cache_resource
def get_llm():
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        openai_api_key=openai_key
    )
    return llm.bind_tools(TOOLS)

# ────────────────────────────────────────────────────────────────
# TOOL-AWARE QUERY
# ────────────────────────────────────────────────────────────────
def query_llm_with_tools(prompt: str) -> str:
    try:
        llm = get_llm()
        response = llm.invoke([HumanMessage(content=prompt)])

        if hasattr(response, "tool_calls") and response.tool_calls:
            results = []
            for call in response.tool_calls:
                tool_fn = next(t for t in TOOLS if t.name == call["name"])
                results.append(tool_fn.invoke(call["args"]))
            return "\n".join(results)

        return response.content

    except Exception as e:
        return f"❌ AI error: {e}"

# ────────────────────────────────────────────────────────────────
# Deterministic Logic (unchanged)
# ────────────────────────────────────────────────────────────────
def adjust_category_forecast(prompt, session_state):
    for cat in session_state:
        if cat.lower() in prompt.lower():
            if "increase" in prompt:
                session_state[cat] *= 1.10
                return f"Increased {cat} by 10%."
            elif "decrease" in prompt:
                session_state[cat] *= 0.90
                return f"Decreased {cat} by 10%."
    return "Which category should be adjusted?"

def report_summary(_, session_state):
    total = sum(v for k, v in session_state.items() if k != "Revenue")
    ratio = total / session_state["Revenue"] * 100
    return f"IT Spend: ${total:,.0f} ({ratio:.2f}% of revenue)"

# ────────────────────────────────────────────────────────────────
# Main Handler
# ────────────────────────────────────────────────────────────────
def handle_ai_consultation(user_prompt, session_state, role="CIO", goal="Optimize Costs"):
    intent = classify_intent(user_prompt)

    if intent == "report_summary":
        return report_summary(user_prompt, session_state)
    if intent == "adjust_category_forecast":
        return adjust_category_forecast(user_prompt, session_state)

    full_prompt = f"You are advising a {role} focused on {goal}. {user_prompt}"
    return query_llm_with_tools(full_prompt)

def generate_ai_maturity_recommendation_with_products(category: str) -> dict:
    try:
        response = supabase.table("ai_product_recommendations").select("*").eq("category", category).execute()
        if response.data:
            st.info(f"✅ Using cached recommendation for '{category}' from Supabase.")
            return {
                "recommendation": response.data[0]["recommendation"],
                "products": response.data[0]["products"]
            }

        tavily = TavilyClient(api_key=tavily_key)
        query = f"Top enterprise tools or platforms for improving {category} AI maturity"
        results = tavily.search(query, max_results=5)

        combined = " ".join([
            f"{r.get('title', '')} — {r.get('snippet', '')}" for r in results if isinstance(r, dict) and r.get("snippet")
        ])

        prompt = (
            f"Based on this content:\n{combined}\n\n"
            f"List 3–5 tools for '{category}' in AI maturity. Format as JSON:\n"
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
        recommendation = (
            f"These tools are well-suited for improving **{category}** maturity. "
            "Focus on high-suitability tools first."
        )

        # Save to Supabase
        supabase.table("ai_product_recommendations").insert({
            "category": category,
            "recommendation": recommendation,
            "products": parsed,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        return {"recommendation": recommendation, "products": parsed}

    except Exception as e:
        st.error(f"❌ Error generating AI maturity recommendation: {e}")
        return {"recommendation": "Unable to generate recommendation.", "products": []}

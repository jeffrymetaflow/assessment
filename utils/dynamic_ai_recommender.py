import os
import re
import ast
import json
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search.tool import TavilySearchResults

# ✅ Load API keys from Streamlit secrets or environment
openai_key = st.secrets.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
tavily_key = st.secrets.get("tavily_api_key") or os.getenv("TAVILY_API_KEY")

# ✅ Ensure Tavily key is set in the environment
os.environ["TAVILY_API_KEY"] = tavily_key

# ✅ Instantiate LLM and search tool
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=openai_key)
tavily = TavilySearchResults()

def get_dynamic_product_recommendations(category: str):
    """
    Retrieve a list of tools for the given AI maturity category using Tavily or fallback to OpenAI.
    Each item returned will include: name, features, price_estimate, and source.
    """
    query = f"Top enterprise software tools for {category} in AI maturity"
    results = tavily.run(query)

    if results and isinstance(results, list):
        product_list = []
        for item in results[:5]:
            title = item.get("title", "Unknown")
            snippet = item.get("snippet", "")
            url = item.get("url", "")
            price_match = re.search(r"\$\d{1,3}(?:,\d{3})*(?:/yr| per year)?", snippet)
            price = price_match.group(0) if price_match else "N/A"

            product_list.append({
                "name": title.strip(),
                "features": snippet[:120] + "...",
                "price_estimate": price,
                "source": url
            })

        if product_list:
            return product_list

    # 🔁 Fallback to OpenAI GPT if Tavily fails or returns no useful content
    fallback_prompt = (
        f"List 3-5 enterprise-grade AI tools that help improve the '{category}' dimension in AI maturity. "
        f"For each tool, include: name, top features, estimated price, and a source URL.\n"
        f"Respond ONLY in valid JSON like this: "
        f"[{{'name': '', 'features': '', 'price_estimate': '', 'source': ''}}]"
    )

    try:
        response = llm.invoke(fallback_prompt)
        response_text = response.content.strip()

        # Clean GPT formatting artifacts
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()

        # Try loading JSON directly
        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError:
            # Try safe literal eval fallback
            parsed = ast.literal_eval(response_text)

        if isinstance(parsed, list):
            return parsed

    except Exception as e:
        print("❌ Fallback OpenAI parsing failed:", e)

    return []

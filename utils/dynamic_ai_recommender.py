import os
import re
import streamlit as st
import json
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search.tool import TavilySearchResults

# Load and authenticate API keys
openai_key = st.secrets.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
tavily_key = st.secrets.get("tavily_api_key") or os.getenv("TAVILY_API_KEY")
os.environ["TAVILY_API_KEY"] = tavily_key

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=openai_key)
tavily = TavilySearchResults()

def simplify_category(category: str) -> str:
    """
    Normalize overly long category strings for more effective Tavily queries.
    """
    keywords = {
        "Data Management": "AI data management tools",
        "Ethics": "AI governance platforms",
        "Infrastructure": "AI infrastructure platforms",
        "Strategy": "AI strategic planning software",
        "Talent": "AI upskilling platforms",
    }
    for k, v in keywords.items():
        if k.lower() in category.lower():
            return v
    return f"AI maturity tools for {category}"

def get_dynamic_product_recommendations(category: str):
    """
    Attempts to retrieve product suggestions from Tavily, with fallback to OpenAI.
    """
    query = simplify_category(category)
    print(f"🔎 Tavily search query: {query}")

    results = tavily.run(query)
    print("🔍 Tavily raw response:", results)

    if results and isinstance(results, list):
        product_list = []
        for item in results[:5]:
            title = item.get("title", "Unknown")
            snippet = item.get("snippet", "")
            url = item.get("url", "")
            price_match = re.search(r"\$\d{1,3}(?:,\d{3})*(?:\/yr| per year)?", snippet)
            price = price_match.group(0) if price_match else "N/A"

            if len(snippet) > 20:
                product_list.append({
                    "name": title.strip(),
                    "features": snippet[:120] + "...",
                    "price_estimate": price,
                    "source": url
                })

        if product_list:
            return product_list

    # 🔁 Fallback to OpenAI if Tavily fails or yields weak results
    fallback_prompt = (
        f"List 3-5 enterprise-grade AI tools that help improve the '{category}' dimension in AI maturity. "
        f"For each, include: name, top features, estimated price, and a website or source.\n\n"
        f"Respond ONLY in this JSON format: "
        f"[{{'name': '', 'features': '', 'price_estimate': '', 'source': ''}}]"
    )

    try:
        response = llm.invoke(fallback_prompt)
        parsed = json.loads(response.content)
        if isinstance(parsed, list):
            return parsed
    except Exception as e:
        print("❌ Fallback OpenAI parsing failed:", e)

    return []

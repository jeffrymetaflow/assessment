import os
import re
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search.tool import TavilySearchResults

# ✅ Explicit API key loading for Streamlit Cloud
openai_key = st.secrets.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
tavily_key = st.secrets.get("tavily_api_key") or os.getenv("TAVILY_API_KEY")

# ✅ Ensure Tavily is authenticated properly
os.environ["TAVILY_API_KEY"] = tavily_key

# ✅ Instantiate LLM with explicit key
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=openai_key)
tavily = TavilySearchResults()

def get_dynamic_product_recommendations(category: str):
    """
    Search for and return a list of relevant enterprise tools for the given AI maturity category.
    Falls back to LLM if Tavily search yields no usable results.
    """
    query = f"Top enterprise software tools for {category} in AI maturity"
    results = tavily.run(query)

    if results and isinstance(results, list):
        product_list = []
        for item in results[:5]:  # Limit to top 5 results
            title = item.get("title", "Unknown")
            snippet = item.get("snippet", "")
            url = item.get("url", "")
            price_match = re.search(r"\$\d{1,3}(?:,\d{3})*(?:\/yr| per year)?", snippet)
            price = price_match.group(0) if price_match else "N/A"

            product_list.append({
                "name": title.strip(),
                "features": snippet[:120] + "...",
                "price_estimate": price,
                "source": url
            })
        if product_list:
            return product_list

    # 🔁 Fallback to GPT if Tavily fails
    fallback_prompt = (
        f"List 3-5 enterprise-grade AI tools or platforms ideal for the category '{category}' in an AI maturity model. "
        f"For each, include name, top features, and estimated price or cost model. "
        f"Respond in JSON format: [{{'name': '', 'features': '', 'price_estimate': '', 'source': ''}}]"
    )
    response = llm.invoke(fallback_prompt)

    try:
        import json
        parsed = json.loads(response.content)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass

    return []

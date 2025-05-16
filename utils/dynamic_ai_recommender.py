import re
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search.tool import TavilySearchResults

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
tavily = TavilySearchResults()

def get_dynamic_product_recommendations(category: str):
    query = f"Top enterprise software tools for {category} in AI maturity"
    search_results = tavily.run(query)

    recommended = []

    for result in search_results:
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        url = result.get("url", "")
        combined_text = f"{title}. {snippet}"

        # Extract price estimate if mentioned
        price_match = re.search(r"\$\d{1,3}(?:,\d{3})*(?:\/yr| per year)?", combined_text)
        price_estimate = price_match.group(0) if price_match else "N/A"

        # Try to guess product name
        product_name = title.split(" ")[0] if title else "Unknown"

        recommended.append({
            "name": product_name,
            "features": snippet[:120] + "...",
            "price_estimate": price_estimate,
            "suitability": "Inferred"
        })

    return recommended[:5]

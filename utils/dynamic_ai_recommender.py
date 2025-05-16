import re
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search.tool import TavilySearchResults

# Initialize LLM and search tool
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
tavily = TavilySearchResults()

def get_dynamic_product_recommendations(category: str):
    """
    Search for and return a list of relevant enterprise tools for the given AI maturity category.
    Each product includes name, features, price estimate, and source URL.
    """
    query = f"Top enterprise software tools for {category} in AI maturity"
    results = tavily.run(query)

    if not results or not isinstance(results, list):
        return []

    product_list = []

    for item in results[:5]:  # Limit to top 5 results
        title = item.get("title", "Unknown")
        snippet = item.get("snippet", "")
        url = item.get("url", "")

        # Extract price from snippet if available
        price_match = re.search(r"\$\d{1,3}(?:,\d{3})*(?:\/yr| per year)?", snippet)
        price = price_match.group(0) if price_match else "N/A"

        product_list.append({
            "name": title.strip(),
            "features": snippet[:120] + "...",
            "price_estimate": price,
            "source": url
        })

    return product_list

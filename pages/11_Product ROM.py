import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import uuid
import numpy as np
import re
from tavily import TavilyClient
from utils.bootstrap import page_bootstrap
from utils.session_state import initialize_session
initialize_session()
from utils.auth import enforce_login
enforce_login()
from controller.supabase_controller import save_session_to_supabase

st.set_page_config(page_title="Product Recommendations & Budget with AI Lookup", layout="wide")

st.title("🛒 Product Recommendations & Budget Plan (AI Price Lookup)")

# Initialize Tavily client
tavily = TavilyClient(api_key=st.secrets["tavily_api_key"])

# --- AI-powered product price lookup with Supabase caching ---
def lookup_product_price_ai_with_supabase(product_name):
    try:
        # Check Supabase first
        response = supabase.table("product_prices").select("*").eq("product_name", product_name).execute()
        if response.data and len(response.data) > 0:
            cached_price = response.data[0]["price"]
            return cached_price

        # If not found, perform enhanced AI lookup
        query = f"{product_name} enterprise software pricing OR list price site:{product_name.split()[0]}.com"
        results = tavily.search(query, max_results=5)
        for result in results:
            combined_text = f"{result.get('title', '')} {result.get('snippet', '')}"
            price_match = re.search(r'\$[0-9,]+', combined_text)
            if price_match:
                price = float(price_match.group(0).replace('$','').replace(',',''))
                # Store new price in Supabase
                supabase.table("product_prices").insert({
                    "product_name": product_name,
                    "price": price
                }).execute()
                return price
        return None
    except Exception as e:
        print(f"AI lookup failed for {product_name}: {e}")
        return None
    except Exception as e:
        print(f"AI lookup failed for {product_name}: {e}")
        return None

# --- Safely extract and enrich product recommendations ---
recommendations = []
if "it_maturity_recommendations" in st.session_state:
    recommendations.extend(st.session_state["it_maturity_recommendations"])
if "cyber_maturity_recommendations" in st.session_state:
    recommendations.extend(st.session_state["cyber_maturity_recommendations"])
if "ai_maturity_recommendations" in st.session_state:
    st.subheader("🛠️ Suggested AI Tools and Services")

def assign_phase(score):
    if score < 50:
        return "Q1"
    elif score < 80:
        return "Q2"
    else:
        return "Q3"

products_data = []
for rec in recommendations:
    if "products" in rec and rec["products"]:
        for product_name in rec["products"]:
            price = lookup_product_price_ai_with_supabase(product_name)
            products_data.append({
                "Quarter": assign_phase(rec["score"]),
                "Category": rec["category"],
                "Product": product_name,
                "List Price ($)": round(price, 2) if price else "N/A",
                "% Discount": 0,
                "Discounted Price ($)": round(price, 2) if price else "N/A",
            })

# --- Display table with interactive discount ---
if products_data:
    product_df = pd.DataFrame(products_data)

    for i in range(len(product_df)):
        if product_df.at[i, "List Price ($)"] != "N/A":
            discount = st.number_input(
                f"Discount % for {product_df.at[i, 'Product']}",
                min_value=0, max_value=100, value=int(product_df.at[i, "% Discount"]), key=f"discount_{i}"
            )
            product_df.at[i, "% Discount"] = discount
            discounted_price = product_df.at[i, "List Price ($)"] * (1 - discount / 100)
            product_df.at[i, "Discounted Price ($)"] = round(discounted_price, 2)

    st.dataframe(product_df, use_container_width=True)

    total_cost = product_df[product_df["Discounted Price ($)"] != "N/A"]["Discounted Price ($)"].sum()
    st.markdown(f"### 💰 Estimated Total Budget After Discounts: **${total_cost:,.2f}**")
else:
    st.info("No products found in recommendations.")

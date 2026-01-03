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
from utils.auth import enforce_login
from controller.supabase_controller import save_session_to_supabase
from utils.supabase_client import get_supabase

# --- Setup ---
st.set_page_config(page_title="Product Recommendations & Budget with AI Lookup", layout="wide")
initialize_session()
page_bootstrap(current_page="Product ROM")
enforce_login()

st.title("🛒 Product Recommendations & Budget Plan (AI Price Lookup)")

# --- Tavily + Supabase Init ---
tavily = TavilyClient(api_key=st.secrets["tavily_api_key"])
supabase = get_supabase()

# --- AI Lookup + Supabase Caching ---
def lookup_product_price_ai_with_supabase(product_name):
    try:
        # 1. Check Supabase cache
        response = supabase.table("product_prices").select("*").eq("product_name", product_name).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]["price"]

        # 2. Tavily-enhanced search
        query = f"{product_name} enterprise software pricing OR list price site:{product_name.split()[0]}.com"
        results = tavily.search(query, max_results=5)
        for result in results:
            combined_text = f"{result.get('title', '')} {result.get('snippet', '')}"
            match = re.search(r'\$[0-9,]+', combined_text)
            if match:
                price = float(match.group(0).replace('$', '').replace(',', ''))
                # 3. Cache in Supabase
                supabase.table("product_prices").insert({
                    "product_name": product_name,
                    "price": price
                }).execute()
                return price
        return None
    except Exception as e:
        print(f"[Price Lookup Failed] {product_name}: {e}")
        return None

# --- Load Recommendations ---
recommendations = []

for source_key, label in [
    ("it_maturity_recommendations", "IT"),
    ("cyber_maturity_recommendations", "Cyber"),
    ("ai_maturity_recommendations", "AI"),
]:
    for r in st.session_state.get(source_key, []):
        r["source"] = label
        recommendations.append(r)

# --- Quarter Logic by Score ---
def assign_phase(score):
    if score < 50:
        return "Q1"
    elif score < 80:
        return "Q2"
    return "Q3"

# --- Enrich Product Data ---
products_data = []
for rec in recommendations:
    score = rec.get("score", 0)
    category = rec.get("category", "General")
    source = rec.get("source", "Unknown")

    if "products" in rec:
        for p in rec["products"]:
            if isinstance(p, dict):
                product_name = p.get("name", "Unnamed")
                est_price = p.get("price_estimate", "N/A")
            else:
                product_name = str(p)
                est_price = "N/A"

            ai_price = lookup_product_price_ai_with_supabase(product_name)

            products_data.append({
                "Quarter": assign_phase(score),
                "Category": category,
                "Product": product_name,
                "Estimated Price (from AI)": est_price,
                "List Price ($)": round(ai_price, 2) if ai_price else "N/A",
                "% Discount": 0,
                "Discounted Price ($)": round(ai_price, 2) if ai_price else "N/A",
                "Source": source
            })

# --- Display Interactive Table ---
if products_data:
    product_df = pd.DataFrame(products_data)

    for i in range(len(product_df)):
        if product_df.at[i, "List Price ($)"] != "N/A":
            default_discount = int(product_df.at[i, "% Discount"])
            discount = st.number_input(
                f"Discount % for {product_df.at[i, 'Product']}",
                min_value=0, max_value=100, value=default_discount,
                key=f"discount_{i}"
            )
            product_df.at[i, "% Discount"] = discount
            list_price = product_df.at[i, "List Price ($)"]
            discounted_price = list_price * (1 - discount / 100)
            product_df.at[i, "Discounted Price ($)"] = round(discounted_price, 2)

    st.dataframe(product_df, use_container_width=True)

    total_cost = product_df[product_df["Discounted Price ($)"] != "N/A"]["Discounted Price ($)"].sum()
    st.markdown(f"### 💰 Estimated Total Budget After Discounts: **${total_cost:,.2f}**")
else:
    st.info("No products found in recommendations.")

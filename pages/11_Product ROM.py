import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import uuid
import numpy as np
from utils.bootstrap import page_bootstrap
from utils.session_state import initialize_session
initialize_session()
from utils.auth import enforce_login
enforce_login()
from controller.supabase_controller import save_session_to_supabase

st.set_page_config(page_title="Product Recommendations & Budget", layout="wide")

st.title("🛒 Product Recommendations & Budget Plan")

# --- Safely restore recommendations from session ---
recommendations = []

if "it_maturity_recommendations" in st.session_state:
    recommendations.extend(st.session_state["it_maturity_recommendations"])

if "cyber_maturity_recommendations" in st.session_state:
    recommendations.extend(st.session_state["cyber_maturity_recommendations"])

if not recommendations:
    st.warning("⚠️ No recommendations found. Please complete the assessments first.")
    st.stop()

# --- Helper to assign phase ---
def assign_phase(score):
    if score < 50:
        return "Q1"
    elif score < 80:
        return "Q2"
    else:
        return "Q3"

# --- Extract product recommendations ---
products_data = []
for rec in recommendations:
    if "products" in rec and rec["products"]:
        for product in rec["products"]:
            products_data.append({
                "Quarter": assign_phase(rec["score"]),
                "Category": rec["category"],
                "Product": product["name"],
                "List Price ($)": product["list_price"],
                "% Discount": 0,  # Default manual input
                "Discounted Price ($)": product["list_price"],
            })

if products_data:
    product_df = pd.DataFrame(products_data)

    # Editable Discount columns
    for i in range(len(product_df)):
        discount = st.number_input(
            f"Discount % for {product_df.at[i, 'Product']}",
            min_value=0, max_value=100, value=int(product_df.at[i, "% Discount"]), key=f"discount_{i}"
        )
        product_df.at[i, "% Discount"] = discount
        discounted_price = product_df.at[i, "List Price ($)"] * (1 - discount / 100)
        product_df.at[i, "Discounted Price ($)"] = round(discounted_price, 2)

    st.dataframe(product_df, use_container_width=True)

    # Total budget summary
    total_cost = product_df["Discounted Price ($)"].sum()
    st.markdown(f"### 💰 Estimated Total Budget After Discounts: **${total_cost:,.2f}**")
else:
    st.info("No products found in recommendations.")

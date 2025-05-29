import streamlit as st
st.set_page_config(page_title="Strategic Roadmap", layout="wide")

import pandas as pd
import numpy as np
from utils.bootstrap import page_bootstrap
from utils.session_state import initialize_session
from utils.auth import enforce_login
from controller.supabase_controller import save_session_to_supabase
from utils.supabase_client import get_supabase

initialize_session()
page_bootstrap(current_page="Strategic Roadmap")
enforce_login()

st.title("📊 Strategic_Roadmap")

st.markdown("""
### Strategic Roadmap
Based on your assessment scores and ITRM trajectory, this roadmap offers recommended actions.
""")

# --- AI-enriched recommendations ---
recommendations = []
if "it_maturity_recommendations" in st.session_state:
    for r in st.session_state["it_maturity_recommendations"]:
        r["source"] = "IT"

if "cyber_maturity_recommendations" in st.session_state:
    for r in st.session_state["cyber_maturity_recommendations"]:
        r["source"] = "Cyber"

if "ai_maturity_recommendations" in st.session_state:
    for r in st.session_state["ai_maturity_recommendations"]:
        r["source"] = "AI"

recommendations = (
    st.session_state.get("it_maturity_recommendations", []) +
    st.session_state.get("cyber_maturity_recommendations", []) +
    st.session_state.get("ai_maturity_recommendations", [])
)

if not recommendations:
    st.warning("⚠️ No recommendations found. Please complete the IT Maturity Assessment first.")
    st.stop()

# --- Nexus One Supplier Recommendations ---
st.subheader("🔗 Nexus One Supplier Recommendations")
supabase = get_supabase()

# Dynamically infer needs
low_score_cats = roadmap_df.loc[roadmap_df["Score"] < 80, "Category"].unique().tolist()
compliance_need = "HIPAA" if "compliance" in roadmap_df["Action Item"].str.lower().to_string().lower() else ""
seat_range_need = "1000+" if "scale" in roadmap_df["Action Item"].str.lower().to_string().lower() else ""
teams_support_need = "Direct routing" if "teams" in roadmap_df["Action Item"].str.lower().to_string().lower() else ""

response = supabase.table("suppliers").select("*").execute()
suppliers = response.data

def score_supplier(s):
    score = 0
    if compliance_need and compliance_need.lower() in (s.get("compliance") or "").lower():
        score += 1
    if seat_range_need and seat_range_need in (s.get("seat_range") or ""):
        score += 1
    if teams_support_need and teams_support_need.lower() in (s.get("teams_support") or "").lower():
        score += 1
    return score

scored = sorted(suppliers, key=score_supplier, reverse=True)
recommended_suppliers = [
    s for s in scored
    if any(cat.lower() in (s.get("mapped_categories") or "").lower() for cat in low_score_cats)
][:3]

if recommended_suppliers:
    st.markdown("### 🧩 Matched Suppliers")
    top_score = score_supplier(recommended_suppliers[0])
    for idx, supplier in enumerate(recommended_suppliers):
        with st.container():
            cols = st.columns([2, 6])
            with cols[0]:
                st.image(supplier.get("logo_url", "https://via.placeholder.com/100"), width=100)
            with cols[1]:
                top_match_label = "🟢 Top Match" if score_supplier(supplier) == top_score and idx == 0 else ""
                st.markdown(f"### {supplier.get('supplier_name', 'Supplier')} {top_match_label}")
                st.markdown(f"- **Compliance**: {supplier.get('compliance')}")
                st.markdown(f"- **Teams Support**: {supplier.get('teams_support')}")
                st.markdown(f"- **Seat Range**: {supplier.get('seat_range')}")
                if supplier.get("website"):
                    st.markdown(f"- [🌐 Visit Website]({supplier.get('website')})")
            with st.expander("📨 Request Quote"):
                st.markdown("""
                <iframe src="https://share.hsforms.com/1aBcD-ExampleEmbedCode" width="100%" height="600" style="border:0;" frameborder="0" scrolling="no"></iframe>
                """, unsafe_allow_html=True)
else:
    st.info("No matching Nexus One suppliers found for the current profile.")

if st.button("💾 Save Project to Supabase"):
    save_session_to_supabase()

# --- Last Save Timestamp ---
if "project_data" in st.session_state:
    last_saved = st.session_state["project_data"].get("last_saved")
    if last_saved:
        st.caption(f"🕒 Last saved: {last_saved}")

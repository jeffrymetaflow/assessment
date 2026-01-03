import streamlit as st
import pandas as pd
from utils.bootstrap import page_bootstrap
from utils.session_state import initialize_session
from utils.auth import enforce_login
from controller.supabase_controller import save_session_to_supabase
from utils.supabase_client import get_supabase

# --- Setup ---
st.set_page_config(page_title="Product", layout="wide")
initialize_session()
page_bootstrap(current_page="Product")
enforce_login()

st.title("🤖 Product Supplier Intelligence")

st.markdown("""
### Strategic Supplier Matching  
Based on your assessment results, we match your IT gaps with curated suppliers from the Nexus One ecosystem.
""")

# --- Load Recommendations from Session ---
recommendations = []
for source_key, source_label in [
    ("it_maturity_recommendations", "IT"),
    ("cyber_maturity_recommendations", "Cyber"),
    ("ai_maturity_recommendations", "AI"),
]:
    if source_key in st.session_state:
        for r in st.session_state[source_key]:
            r["source"] = source_label
            r["category"] = r.get("category", "General")
            r["Score"] = r.get("score", 0)
        recommendations += st.session_state[source_key]

# --- Validate ---
if not recommendations:
    st.warning("⚠️ No recommendations found. Please complete the assessments first.")
    st.stop()

# --- Normalize & Analyze Recommendations ---
roadmap_df = pd.DataFrame(recommendations)
roadmap_df["category"] = roadmap_df["category"].fillna("General")
roadmap_df["Score"] = pd.to_numeric(roadmap_df["Score"], errors="coerce").fillna(0)

# --- Check if compliance needs are mentioned ---
compliance_text_block = roadmap_df.get("recommendation", pd.Series(dtype=str)).str.cat(sep=' ').lower()
compliance_need = "HIPAA" if "compliance" in compliance_text_block else ""

# Identify low-maturity categories
low_score_cats = roadmap_df[roadmap_df["Score"] < 80]["category"].unique().tolist()

# --- Load Suppliers from Supabase ---
supabase = get_supabase()
response = supabase.table("suppliers").select("*").execute()
suppliers = response.data or []

# --- Define Scoring Logic ---
seat_range_need = ""       # placeholder for future filter
teams_support_need = ""    # placeholder for future filter

def score_supplier(supplier):
    score = 0
    compliance = (supplier.get("compliance") or "").lower()
    mapped_cats = (supplier.get("mapped_categories") or "").lower()
    teams_support = (supplier.get("teams_support") or "").lower()
    seat_range = supplier.get("seat_range") or ""

    if compliance_need and compliance_need.lower() in compliance:
        score += 1
    if seat_range_need and seat_range_need in seat_range:
        score += 1
    if teams_support_need and teams_support_need.lower() in teams_support:
        score += 1
    if any(cat.lower() in mapped_cats for cat in low_score_cats):
        score += 2  # Core match
    return score

# --- Filter + Score Suppliers ---
scored = sorted(suppliers, key=score_supplier, reverse=True)
scored_suppliers = [s for s in scored if score_supplier(s) > 0]

# --- Supplier Display ---
st.subheader("🔗 Nexus One Supplier Recommendations")

show_all = st.checkbox("Show all matching suppliers")

if not scored_suppliers:
    st.info("No matching Nexus One suppliers found for the current profile.")
else:
    top_score = score_supplier(scored_suppliers[0])
    displayed = scored_suppliers if show_all else scored_suppliers[:3]

    st.markdown("### 🧩 Matched Suppliers")

    for idx, supplier in enumerate(displayed):
        with st.container():
            cols = st.columns([2, 6])

            # Logo
            with cols[0]:
                logo_url = supplier.get("logo_url", "")
                if not logo_url.startswith("http"):
                    logo_url = "https://via.placeholder.com/100"
                st.image(logo_url, width=100)

            # Details
            with cols[1]:
                supplier_name = supplier.get("supplier_name", "Unnamed Supplier")
                score = score_supplier(supplier)
                top_match_label = "🟢 Top Match" if score == top_score and not show_all and idx == 0 else ""

                st.markdown(f"### {supplier_name} {top_match_label}")
                st.markdown(f"- **Compliance**: {supplier.get('compliance', 'N/A')}")
                st.markdown(f"- **Mapped Categories**: {supplier.get('mapped_categories', 'N/A')}")

                matched = [
                    cat for cat in low_score_cats
                    if cat.lower() in (supplier.get("mapped_categories") or "").lower()
                ]
                if matched:
                    st.markdown(f"- **Matched Needs**: `{', '.join(matched)}`")

                if supplier.get("website"):
                    st.markdown(f"- [🌐 Visit Website]({supplier['website']})")

            with st.expander("📨 Request Quote"):
                st.markdown("""
                <iframe src="https://share.hsforms.com/1aBcD-ExampleEmbedCode" width="100%" height="600" style="border:0;" frameborder="0" scrolling="no"></iframe>
                """, unsafe_allow_html=True)

# --- Save Button ---
if st.button("💾 Save Project to Supabase"):
    save_session_to_supabase()

if "project_data" in st.session_state:
    last_saved = st.session_state["project_data"].get("last_saved")
    if last_saved:
        st.caption(f"🕒 Last saved: {last_saved}")

import streamlit as st
st.set_page_config(page_title="Nexus One", layout="wide")

import pandas as pd
from utils.bootstrap import page_bootstrap
from utils.session_state import initialize_session
from utils.auth import enforce_login
from controller.supabase_controller import save_session_to_supabase
from utils.supabase_client import get_supabase

# --- Init
initialize_session()
page_bootstrap(current_page="Nexus One")
enforce_login()

st.title("🤖 Nexus One Supplier Intelligence")

st.markdown("""
### Strategic Supplier Matching  
Based on your assessment results, we match your IT gaps with curated suppliers from the Nexus One ecosystem.
""")

# --- AI-enriched recommendations
recommendations = []
for source_key, source_label in [
    ("it_maturity_recommendations", "IT"),
    ("cyber_maturity_recommendations", "Cyber"),
    ("ai_maturity_recommendations", "AI"),
]:
    if source_key in st.session_state:
        for r in st.session_state[source_key]:
            r["source"] = source_label
            r["category"] = r.get("category", "General")  # Ensure category is populated
            r["Score"] = r.get("Score", 0)  # Ensure Score is included
        recommendations += st.session_state[source_key]

# --- Validate and prep
if not recommendations:
    st.warning("⚠️ No recommendations found. Please complete the assessments first.")
    st.stop()

roadmap_df = pd.DataFrame(recommendations)
roadmap_df["category"] = roadmap_df["category"].fillna("General")

# --- Ensure Score is numeric
roadmap_df["Score"] = pd.to_numeric(roadmap_df["Score"], errors="coerce")

# --- Safely extract compliance need
available_columns = roadmap_df.columns.tolist()
target_column = "recommendation" if "recommendation" in available_columns else (
    "Action Item" if "Action Item" in available_columns else None
)

if target_column:
    action_text = roadmap_df[target_column].str.lower().to_string().lower()
    compliance_need = "HIPAA" if "compliance" in action_text else ""
else:
    compliance_need = ""

# Identify low-score areas
low_score_df = roadmap_df[roadmap_df["Score"] < 80]
low_score_cats = low_score_df["category"].unique().tolist()

# --- Category Score Heatmap
st.subheader("📉 Heatmap of Assessment Gaps by Category")
valid_scores = roadmap_df.dropna(subset=["Score"])

if not valid_scores.empty:
    category_scores = valid_scores.groupby("category")["Score"].mean().sort_values()
    st.bar_chart(category_scores)
else:
    st.info("No valid category scores available for heatmap display.")

# --- Load suppliers from Supabase
supabase = get_supabase()
response = supabase.table("suppliers").select("*").execute()
suppliers = response.data

# Placeholder for future filters
seat_range_need = ""
teams_support_need = ""

def score_supplier(s):
    score = 0
    if compliance_need and compliance_need.lower() in (s.get("compliance") or "").lower():
        score += 1
    if seat_range_need and seat_range_need in (s.get("seat_range") or ""):
        score += 1
    if teams_support_need and teams_support_need.lower() in (s.get("teams_support") or "").lower():
        score += 1
    if any(cat.lower() in (s.get("mapped_categories") or "").lower() for cat in low_score_cats):
        score += 2  # core match weight
    return score

scored = sorted(suppliers, key=score_supplier, reverse=True)
recommended_suppliers = [s for s in scored if score_supplier(s) > 0][:3]

# --- Display results
st.subheader("🔗 Nexus One Supplier Recommendations")

if recommended_suppliers:
    st.markdown("### 🧩 Matched Suppliers")
    top_score = score_supplier(recommended_suppliers[0])

    for idx, supplier in enumerate(recommended_suppliers):
        with st.container():
            cols = st.columns([2, 6])
            with cols[0]:
                logo_url = supplier.get("logo_url")
                if not logo_url or not logo_url.startswith("http"):
                    logo_url = "https://via.placeholder.com/100"
                st.image(logo_url, width=100)

            with cols[1]:
                top_match_label = "🟢 Top Match" if score_supplier(supplier) == top_score and idx == 0 else ""
                st.markdown(f"### {supplier.get('supplier_name', 'Supplier')} {top_match_label}")
                st.markdown(f"- **Compliance**: {supplier.get('compliance') or 'N/A'}")
                st.markdown(f"- **Mapped Categories**: {supplier.get('mapped_categories') or 'N/A'}")

                # Show matched categories explicitly
                matched = [
                    cat for cat in low_score_cats
                    if cat.lower() in (supplier.get("mapped_categories") or "").lower()
                ]
                if matched:
                    st.markdown(f"- **Matched Needs**: `{', '.join(matched)}`")

                if supplier.get("website"):
                    st.markdown(f"- [🌐 Visit Website]({supplier.get('website')})")

            with st.expander("📨 Request Quote"):
                st.markdown("""
                <iframe src="https://share.hsforms.com/1aBcD-ExampleEmbedCode" width="100%" height="600" style="border:0;" frameborder="0" scrolling="no"></iframe>
                """, unsafe_allow_html=True)
else:
    st.info("No matching Nexus One suppliers found for the current profile.")

# --- Save project state
if st.button("💾 Save Project to Supabase"):
    save_session_to_supabase()

# --- Last save timestamp
if "project_data" in st.session_state:
    last_saved = st.session_state["project_data"].get("last_saved")
    if last_saved:
        st.caption(f"🕒 Last saved: {last_saved}")

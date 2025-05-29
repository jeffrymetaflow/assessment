import streamlit as st
import pandas as pd
import numpy as np
from utils.bootstrap import page_bootstrap
from utils.session_state import initialize_session
from utils.auth import enforce_login
from controller.supabase_controller import save_session_to_supabase, get_supabase_client

initialize_session()
page_bootstrap(current_page="Strategic Roadmap")
enforce_login()

st.set_page_config(page_title="Strategic Roadmap", layout="wide")
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

# --- Build Roadmap Table ---
def assign_phase(score):
    if score < 50:
        return "Q1"
    elif score < 80:
        return "Q2"
    else:
        return "Q3"

roadmap_data = []
for rec in recommendations:
    roadmap_data.append({
        "Quarter": assign_phase(rec.get("score", 0)),
        "Category": rec.get("category", ""),
        "Action Item": rec.get("recommendation", "Maintain and enhance automation"),
        "Products": ", ".join([p.get("name") for p in rec.get("products", []) if isinstance(p, dict)]) if rec.get("products") else "N/A",
        "Source": rec.get("source", "Unknown"),
        "Score": rec.get("score", 0)
    })

roadmap_df = pd.DataFrame(roadmap_data)
st.subheader("📅 Strategic Timeline by Quarter")
st.dataframe(roadmap_df.drop(columns=["Score"]), use_container_width=True)

st.subheader("✅ Progress Tracker")
for quarter in sorted(roadmap_df["Quarter"].unique()):
    st.markdown(f"#### {quarter}")
    for _, row in roadmap_df[roadmap_df["Quarter"] == quarter].iterrows():
        st.checkbox(f"{row['Category']} – {row['Action Item']}", key=f"{row['Category']}_{quarter}")

# --- Nexus One Supplier Recommendations ---
st.subheader("🔗 Nexus One Supplier Recommendations")
supabase = get_supabase_client()

# Dynamically infer needs
target_category = roadmap_df.loc[roadmap_df["Score"] < 80, "Category"].mode().values[0] if not roadmap_df[roadmap_df["Score"] < 80].empty else "UCaaS"
compliance_need = "HIPAA" if "compliance" in roadmap_df["Action Item"].str.lower().to_string().lower() else ""
seat_range_need = "1000+" if "scale" in roadmap_df["Action Item"].str.lower().to_string().lower() else ""
teams_support_need = "Direct routing" if "teams" in roadmap_df["Action Item"].str.lower().to_string().lower() else ""

response = supabase.table("suppliers").select("*").eq("category", target_category).execute()
suppliers = response.data

recommended_suppliers = [
    s for s in suppliers
    if (compliance_need in (s.get("compliance") or "")) and
       (seat_range_need in (s.get("seat_range") or "")) and
       (teams_support_need in (s.get("teams_support") or ""))
][:3]

if recommended_suppliers:
    st.markdown("### 🧩 Matched Suppliers")
    for supplier in recommended_suppliers:
        with st.container():
            st.markdown(f"**{supplier.get('supplier_name')}**")
            cols = st.columns([2, 5])
            with cols[0]:
                st.image(supplier.get("logo_url", "https://via.placeholder.com/100"), width=100)
            with cols[1]:
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


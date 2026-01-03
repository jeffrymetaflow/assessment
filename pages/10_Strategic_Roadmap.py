import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import uuid
import numpy as np

from utils.bootstrap import page_bootstrap
from utils.session_state import initialize_session
from utils.auth import enforce_login
from controller.supabase_controller import save_session_to_supabase

# --- Initialize ---
initialize_session()
enforce_login()
page_bootstrap(current_page="Strategic Roadmap")
st.set_page_config(page_title="Strategic Roadmap", layout="wide")
st.title("📊 Strategic Roadmap")

st.markdown("""
### Strategic Roadmap  
Based on your assessment scores and ITRM trajectory, this roadmap offers recommended actions.
""")

# --- Collect All Recommendations ---
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
    st.warning("⚠️ No recommendations found. Please complete at least one assessment.")
    st.stop()

# --- Assign roadmap phase by score ---
def assign_phase(score):
    if score < 50:
        return "Q1"
    elif score < 80:
        return "Q2"
    else:
        return "Q3"

roadmap_data = []
for rec in recommendations:
    action = rec.get("recommendation", "Maintain and enhance automation")

    # Safer product name extraction
    product_names = ", ".join([
        p.get("name") or p.get("Product") or "Unnamed Product"
        for p in rec.get("products", []) if isinstance(p, dict)
    ]) if rec.get("products") else "N/A"

    roadmap_data.append({
        "Quarter": assign_phase(rec["score"]),
        "Category": rec["category"],
        "Action Item": action,
        "Products": product_names,
        "Source": rec.get("source", "Unknown")
    })

# --- Build Roadmap Table ---
roadmap_df = pd.DataFrame(roadmap_data).sort_values(by=["Quarter", "Category"])

st.subheader("📅 Strategic Timeline by Quarter")
st.dataframe(roadmap_df, use_container_width=True)

# --- Checkbox Tracker ---
st.subheader("✅ Progress Tracker")
for quarter in sorted(roadmap_df["Quarter"].unique()):
    st.markdown(f"#### {quarter}")
    for _, row in roadmap_df[roadmap_df["Quarter"] == quarter].iterrows():
        st.checkbox(f"{row['Category']} – {row['Action Item']}", key=f"{row['Category']}_{quarter}")

# --- Export Button (Optional) ---
csv_buffer = BytesIO()
roadmap_df.to_csv(csv_buffer, index=False)
st.download_button(
    label="⬇️ Download Roadmap CSV",
    data=csv_buffer.getvalue(),
    file_name="strategic_roadmap.csv",
    mime="text/csv"
)

# --- Save to Supabase ---
if st.button("💾 Save Project to Supabase"):
    save_session_to_supabase()

# --- Show last saved time ---
if "project_data" in st.session_state:
    last_saved = st.session_state["project_data"].get("last_saved")
    if last_saved:
        st.caption(f"🕒 Last saved: {last_saved}")

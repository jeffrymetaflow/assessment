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

# Authenticate and initialize
page_bootstrap(current_page="Strategic Roadmap")
enforce_login()

st.set_page_config(page_title="Strategic Roadmap", layout="wide")
st.title("📊 Strategic_Roadmap")
st.markdown("""
### Strategic Roadmap
Based on your assessment scores and ITRM trajectory, this roadmap offers recommended actions.
""")

# Pull AI-enriched recommendations
recommendations = st.session_state.get("it_maturity_recommendations", [])

if not recommendations:
    st.warning("⚠️ No recommendations found. Please complete the IT Maturity Assessment first.")
    st.stop()

# Assign roadmap phase by category score
def assign_phase(score):
    if score < 50:
        return "Q1"
    elif score < 80:
        return "Q2"
    else:
        return "Q3"

roadmap_data = []
for rec in recommendations:
    if rec["recommendation"]:
        action = rec["recommendation"]
    else:
        action = "Maintain and enhance automation"
    roadmap_data.append({
        "Quarter": assign_phase(rec["score"]),
        "Category": rec["category"],
        "Action Item": action
    })

roadmap_df = pd.DataFrame(roadmap_data)

st.subheader("📅 Strategic Timeline by Quarter")
st.dataframe(roadmap_df, use_container_width=True)

st.subheader("✅ Progress Tracker")
for quarter in sorted(roadmap_df["Quarter"].unique()):
    st.markdown(f"#### {quarter}")
    for _, row in roadmap_df[roadmap_df["Quarter"] == quarter].iterrows():
        st.checkbox(f"{row['Category']} – {row['Action Item']}", key=f"{row['Category']}_{quarter}")

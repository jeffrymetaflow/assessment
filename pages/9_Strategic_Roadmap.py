import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import uuid
import numpy as np
from utils.bootstrap import page_bootstrap

st.set_page_config(page_title="Strategic_Roadmap", layout="wide")
st.title("📈 Strategic_Roadmap")

section = "🧭 Strategic Roadmap"  # Define the variable

page_bootstrap()

# Strategic Roadmap Tab
if section == "🧭 Strategic Roadmap":
    st.title("🧭 Strategic Roadmap")
    st.markdown("""
    Based on your assessment scores and ITRM trajectory, this roadmap offers recommended actions.
    """)

    roadmap_items = []
    checklist = []

    if 'it_maturity_scores' in st.session_state:
        scores = st.session_state.it_maturity_scores
        for _, row in scores.iterrows():
            score = row["Score (%)"]
            cat = row["Category"]
            if score >= 80:
                label = "🟢 Maintain and enhance automation"
                rec = f"🟢 {cat}: Maintain and enhance automation."
            elif score >= 50:
                label = "🟡 Standardize and document processes"
                rec = f"🟡 {cat}: Standardize and document processes."
            else:
                label = "🔴 Prioritize investment and leadership support"
                rec = f"🔴 {cat}: Prioritize investment and leadership support."
            roadmap_items.append((cat, label))
            checklist.append(rec)

    if 'cybersecurity_scores' in st.session_state:
        for control, score in st.session_state.cybersecurity_scores.items():
            if score >= 4:
                label = "✅ Sustain mature practices"
                rec = f"✅ {control}: Sustain mature practices."
            elif score == 3:
                label = "⚠️ Refine documentation and training"
                rec = f"⚠️ {control}: Consider refining documentation and training."
            else:
                label = "❌ Prioritize process implementation and governance"
                rec = f"❌ {control}: Prioritize process implementation and governance."
            roadmap_items.append((control, label))
            checklist.append(rec)

    # Ensure both arrays have the same length
    quarters = ["Q1", "Q2", "Q3", "Q4"] * ((len(roadmap_items) + 3) // 4)
    quarters = quarters[:len(roadmap_items)]  # Trim to match the length of roadmap_items

    # Create DataFrame with proper alignment
    timeline_df = pd.DataFrame({
        "Quarter": quarters,
        "Action Item": roadmap_items  # Ensure matching lengths
    })

    if roadmap_items:
        st.subheader("📅 Strategic Timeline by Quarter")
        timeline_df = timeline_df.dropna().reset_index(drop=True)
        st.dataframe(timeline_df)

        st.subheader("✅ Progress Tracker")
        for quarter in ["Q1", "Q2", "Q3", "Q4"]:
            st.markdown(f"**{quarter}**")
            for item in timeline_df[timeline_df["Quarter"] == quarter]["Action Item"]:
                st.checkbox(f"{item[0]} – {item[1]}", key=f"{quarter}_{item[0]}" )

    if checklist:
        st.markdown("---")
        st.subheader("🗒️ Your Strategic Checklist")
        for item in checklist:
            st.markdown(f"- [ ] {item}")

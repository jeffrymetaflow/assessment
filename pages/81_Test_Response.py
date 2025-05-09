import streamlit as st
import pandas as pd

st.title("🧾 Assessment Review")

if "project_data" not in st.session_state:
    st.warning("No project loaded. Please start from the main page.")
    st.stop()

project = st.session_state["project_data"]

# --- IT Maturity Answers ---
st.header("📘 IT Maturity Assessment")
maturity_answers = project.get("maturity_answers")

if maturity_answers:
    st.caption("Your submitted answers:")
    maturity_df = pd.DataFrame([
        {"Question": k, "Answer": v} for k, v in maturity_answers.items()
    ])
    st.dataframe(maturity_df, use_container_width=True)
else:
    st.info("No maturity assessment answers found.")

# --- Cybersecurity Answers ---
st.header("🛡️ Cybersecurity Assessment")
cyber_answers = project.get("cyber_answers")

if cyber_answers:
    st.caption("Your submitted answers:")
    cyber_df = pd.DataFrame([
        {"Question": k, "Answer": v} for k, v in cyber_answers.items()
    ])
    st.dataframe(cyber_df, use_container_width=True)
else:
    st.info("No cybersecurity assessment answers found.")

# --- Optional Last Saved Info ---
if "last_saved" in project:
    st.caption(f"🕒 Last saved: {project['last_saved']}")

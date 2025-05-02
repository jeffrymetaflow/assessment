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

st.set_page_config(page_title="Cybersecurity_Assessment", layout="wide")
st.title("📈 Cybersecurity_Assessment")

section = "🔐 Cybersecurity Assessment"  # Define the variable

page_bootstrap(current_page="Cybersecurity Assessment")  # Or "Risk Model", etc.

# Cybersecurity Assessment Tab
if section == "🔐 Cybersecurity Assessment":
    st.title("🔐 Cybersecurity Maturity Assessment")
    st.markdown("For more details, visit the [NIST Cybersecurity Framework website](https://www.nist.gov/).")

    st.markdown("""
    **NIST Cybersecurity Framework Functions:**

    - **Identify:** Understand the business context, the resources that support critical functions, and the related cybersecurity risks.
    - **Protect:** Develop and implement safeguards to ensure the delivery of critical services.
    - **Detect:** Identify the occurrence of a cybersecurity event in a timely manner.
    - **Respond:** Take action regarding a detected cybersecurity incident.
    - **Recover:** Maintain plans for resilience and restore capabilities or services impaired due to a cybersecurity incident.
    """)

    nist_controls = [
        "Identify - Asset Management",
        "Protect - Access Control",
        "Protect - Data Security",
        "Detect - Anomalies and Events",
        "Respond - Response Planning",
        "Recover - Recovery Planning"
    ]

    st.markdown("""
Please rate your cybersecurity maturity against the **NIST Cybersecurity Framework** categories. Use the scale below to self-assess how well your organization addresses each area:

- **1 – Not Started**: No formal practices or policies in place.
- **2 – Initial**: Informal practices exist but are not documented or consistent.
- **3 – Developing**: Documented practices exist, but only partially implemented.
- **4 – Managed**: Practices are implemented and actively managed.
- **5 – Optimized**: Practices are well-integrated and continuously improved.
""")

    responses = []
    for control in nist_controls:
        score = st.slider(control, min_value=1, max_value=5, value=3, key=f"cyber_nist_{control}")
        responses.append(score)

    st.session_state.cybersecurity_scores = dict(zip(nist_controls, responses))
    average_score = sum(responses) / len(responses)

    # Maturity Heatmap
    st.subheader("🧭 Maturity Heatmap")
    fig, ax = plt.subplots(figsize=(8, 1))
    ax.imshow([responses], cmap='YlGn', aspect='auto')
    ax.set_xticks(range(len(nist_controls)))
    ax.set_xticklabels(nist_controls, rotation=45, ha="right")
    ax.set_yticks([])
    ax.set_title("NIST Domain Maturity Levels")
    for i, score in enumerate(responses):
        ax.text(i, 0, str(score), va='center', ha='center', color='black')
    st.pyplot(fig)

    st.markdown(f"### 🧮 Overall Cybersecurity Maturity Score: **{average_score:.2f} / 5**")
    st.markdown(f"### 🧮 Overall Cybersecurity Maturity Score: **{average_score:.2f} / 5**")

    if average_score >= 4.5:
        st.success("Excellent maturity. Your cybersecurity posture appears robust.")
    elif average_score >= 3.0:
        st.info("Moderate maturity. Consider targeted improvements in specific areas.")
    else:
        st.warning("Low maturity. Immediate enhancements are recommended to reduce risk.")

    st.subheader("🧩 Automated NIST Category Recommendations")
    recommendations = {
        "Identify - Asset Management": "Ensure a complete and regularly updated inventory of all hardware, software, and data assets.",
        "Protect - Access Control": "Implement strong identity and access management (IAM) protocols with role-based access.",
        "Protect - Data Security": "Apply encryption, secure data storage, and data classification policies.",
        "Detect - Anomalies and Events": "Deploy SIEM tools and configure alerts for anomalous behavior.",
        "Respond - Response Planning": "Establish and routinely test an incident response plan.",
        "Recover - Recovery Planning": "Maintain and validate data backups and recovery procedures." 
    }

    for control, score in zip(nist_controls, responses):
        if score <= 3:
            st.warning(f"🔍 {control}: {recommendations[control]}")
        else:
            st.success(f"✅ {control}: Maturity level is sufficient.")
        st.warning("Low maturity. Immediate enhancements are recommended to reduce risk.")

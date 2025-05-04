import streamlit as st
import pandas as pd
from datetime import date
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

st.set_page_config(page_title="📈 ITRM ROI Summary", layout="wide")
st.title("📈 ITRM ROI Summary")

st.subheader("Client & Assessment Info")
client_name = st.text_input("Client Name", "ACME Corp")
assessment_date = st.date_input("Assessment Date", value=date.today())
analyst_name = st.text_input("ITRM Analyst", "Your Name")
assessment_scope = st.text_input("Assessment Scope", "Full IT Environment")

st.subheader("💰 Financial Impact Summary")
financial_data = {
    "Metric": ["Total Annual IT Spend", "Cloud Cost Growth (3-Year)", "Backup/DR Spend", "Personnel + Automation"],
    "Before ITRM": ["$12.4M", "23% CAGR", "$1.9M", "$4.2M"],
    "After ITRM": ["$10.8M", "12% CAGR", "$1.3M", "$3.7M"],
    "Savings/Improvement": ["$1.6M (↓12.9%)", "↓11%", "$600K savings", "$500K optimization"]
}
st.dataframe(pd.DataFrame(financial_data))

st.subheader("🔐 Risk Reduction Simulation")
risk_data = {
    "Risk Domain": ["Cybersecurity", "DR/BC Maturity", "AIOps/Performance Incidents"],
    "Baseline Risk": ["Medium-High", "42%", "11/year"],
    "Post-Optimization": ["Low-Medium", "81%", "3/year"],
    "Business Impact": ["↓ Exposure to compliance & ransomware", "↑ Resilience; ↓ downtime risk", "↑ Productivity, ↓ firefighting costs"]
}
st.dataframe(pd.DataFrame(risk_data))

st.subheader("🧠 Strategic Maturity Gains")
maturity_data = {
    "Capability Area": ["IT Strategy Alignment", "Cyber Maturity", "Financial Planning Accuracy"],
    "Baseline Score": ["2.1 / 5", "2.3 / 5", "56%"],
    "Target Score": ["4.2 / 5", "4.0 / 5", "90%"],
    "Timeframe": ["6 months", "9 months", "3 months"]
}
st.dataframe(pd.DataFrame(maturity_data))

st.subheader("📊 ROI Dashboard Snapshot")
st.metric(label="3-Year ROI Multiple", value="4.7x")
st.metric(label="Payback Period", value="<6 months")
st.metric(label="Total Estimated Value Realized", value="$6.5M")

st.subheader("🧭 Next Steps")
st.markdown("""
- Implement AI-assisted Roadmap Execution (Q3)  
- Reassess spend categories in 6 months  
- Align IT maturity with cross-department digital transformation goals
""")

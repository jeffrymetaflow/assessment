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

page_bootstrap(current_page="ROI Summary")  # Or "Risk Model", etc.

# Pull shared values
client_name = st.session_state.get("client_name", "ACME Corp")
assessment_date = st.session_state.get("assessment_date", date.today())
analyst_name = st.session_state.get("analyst_name", "Your Name")
assessment_scope = st.session_state.get("assessment_scope", "Full IT Environment")

# Display Client Info
st.subheader("Client & Assessment Info")
st.text_input("Client Name", value=client_name, key="client_name")
st.date_input("Assessment Date", value=assessment_date, key="assessment_date")
st.text_input("ITRM Analyst", value=analyst_name, key="analyst_name")
st.text_input("Assessment Scope", value=assessment_scope, key="assessment_scope")

# Financials
st.subheader("💰 Financial Impact Summary")
it_spend_baseline = st.session_state.get("it_expense", 12400000)
it_spend_optimized = st.session_state.get("optimized_it_expense", 10800000)
cloud_cagr_baseline = st.session_state.get("cloud_cagr_baseline", "23%")
cloud_cagr_optimized = st.session_state.get("cloud_cagr_optimized", "12%")

financial_data = {
    "Metric": ["Total Annual IT Spend", "Cloud Cost Growth (3-Year)"],
    "Before ITRM": [f"${it_spend_baseline / 1e6:.1f}M", cloud_cagr_baseline],
    "After ITRM": [f"${it_spend_optimized / 1e6:.1f}M", cloud_cagr_optimized],
    "Savings/Improvement": [
        f"${(it_spend_baseline - it_spend_optimized) / 1e6:.1f}M (↓{(it_spend_baseline - it_spend_optimized) / it_spend_baseline:.1%})",
        "↓11%"
    ]
}
st.dataframe(pd.DataFrame(financial_data))

# Risk Reduction
st.subheader("🔐 Risk Reduction Simulation")
risk_data = {
    "Risk Domain": ["Cybersecurity", "DR/BC Maturity", "AIOps/Performance Incidents"],
    "Baseline Risk": ["Medium-High", "42%", "11/year"],
    "Post-Optimization": ["Low-Medium", "81%", "3/year"],
    "Business Impact": [
        "↓ Exposure to compliance & ransomware",
        "↑ Resilience; ↓ downtime risk",
        "↑ Productivity, ↓ firefighting costs"
    ]
}
st.dataframe(pd.DataFrame(risk_data))

# Maturity Gains
st.subheader("🧠 Strategic Maturity Gains")
maturity_data = {
    "Capability Area": ["IT Strategy Alignment", "Cyber Maturity", "Financial Planning Accuracy"],
    "Baseline Score": ["2.1 / 5", "2.3 / 5", "56%"],
    "Target Score": ["4.2 / 5", "4.0 / 5", "90%"],
    "Timeframe": ["6 months", "9 months", "3 months"]
}
st.dataframe(pd.DataFrame(maturity_data))

# ROI Dashboard
st.subheader("📊 ROI Dashboard Snapshot")
st.metric(label="3-Year ROI Multiple", value=st.session_state.get("roi_multiple", "4.7x"))
st.metric(label="Payback Period", value=st.session_state.get("payback_period", "<6 months"))
st.metric(label="Total Estimated Value Realized", value=st.session_state.get("estimated_value", "$6.5M"))

# Next Steps
st.subheader("🧭 Next Steps")
st.markdown("""
- Implement AI-assisted Roadmap Execution (Q3)  
- Reassess spend categories in 6 months  
- Align IT maturity with cross-department digital transformation goals
""")

# Function to sanitize text
def clean_text(text):
    return text.replace("→", "->").replace("↓", "down ").replace("↑", "up ")

# ✅ Define safe PDF class using built-in Helvetica font
class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", 'B', 14)
        self.cell(0, 10, "ITRM ROI Summary Report", ln=True, align='C')
        self.ln(5)

    def chapter_title(self, title):
        self.set_font("Helvetica", 'B', 12)
        self.cell(0, 10, title, ln=True, align='L')
        self.ln(2)

    def chapter_body(self, text):
        self.set_font("Helvetica", '', 11)
        self.multi_cell(0, 8, text)
        self.ln()

# ✅ Unicode cleaner
def clean_text(text):
    return text.replace("→", "->").replace("↓", "down ").replace("↑", "up ")

# ✅ PDF Export Trigger
if st.button("📤 Export ROI Summary as PDF"):
    pdf = PDF()
    pdf.add_page()

    # 🧠 Pull key values from session state
    client_name = st.session_state.get("client_name", "ACME Corp")
    assessment_date = str(st.session_state.get("assessment_date", date.today()))
    analyst_name = st.session_state.get("analyst_name", "Your Name")
    assessment_scope = st.session_state.get("assessment_scope", "Full IT Environment")
    roi_multiple = st.session_state.get("roi_multiple", "4.7x")
    payback_period = st.session_state.get("payback_period", "<6 months")
    estimated_value = st.session_state.get("estimated_value", "$6.5M")

    # 🧾 Add each PDF section
    pdf.chapter_title("Client & Assessment Info")
    pdf.chapter_body(clean_text(
        f"Client Name: {client_name}\nAssessment Date: {assessment_date}\nAnalyst: {analyst_name}\nAssessment Scope: {assessment_scope}"
    ))

    pdf.chapter_title("Financial Impact Summary")
    pdf.chapter_body(clean_text(
        "Total Annual IT Spend: $12.4M -> $10.8M (down 12.9%)\n"
        "Cloud Cost Growth (3-Year): 23% CAGR -> 12% CAGR\n"
        "Total Forecasted IT Cost Optimization: $2.7M over 3 years"
    ))

    pdf.chapter_title("Risk Reduction Simulation")
    pdf.chapter_body(clean_text(
        "Cybersecurity: Medium-High -> Low-Medium\n"
        "DR/BC Maturity: 42% -> 81%\n"
        "AIOps/Performance Incidents: 11/year -> 3/year\n"
        "Simulated Revenue at Risk Reduced: $3.4M -> $1.1M"
    ))

    pdf.chapter_title("Strategic Maturity Gains")
    pdf.chapter_body(clean_text(
        "IT Strategy Alignment: 2.1 -> 4.2 (6 months)\n"
        "Cyber Maturity: 2.3 -> 4.0 (9 months)\n"
        "Financial Planning Accuracy: 56% -> 90% (3 months)"
    ))

    pdf.chapter_title("ROI Dashboard Snapshot")
    pdf.chapter_body(clean_text(
        f"3-Year ROI Multiple: {roi_multiple}\nPayback Period: {payback_period}\nTotal Estimated Value Realized: {estimated_value}"
    ))

    pdf.chapter_title("Next Steps")
    pdf.chapter_body(clean_text(
        "- Implement AI-assisted Roadmap Execution (Q3)\n"
        "- Reassess spend categories in 6 months\n"
        "- Align IT maturity with cross-department digital transformation goals"
    ))

    # 💾 Save and offer download
    import io
    
    # Output to in-memory buffer instead of file system
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
    
    st.download_button(
        label="📥 Download ROI Summary PDF",
        data=pdf_buffer,
        file_name="ITRM_ROI_Summary_Report.pdf",
        mime="application/pdf"
    )
                file_name="ITRM_ROI_Summary_Report.pdf",
                mime="application/pdf"
            )

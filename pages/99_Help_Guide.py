import streamlit as st
import base64
from utils.bootstrap import page_bootstrap
from utils.session_state import initialize_session
initialize_session()
from utils.auth import enforce_login
enforce_login()


st.set_page_config(page_title="📘 ITRM Help Guide", layout="wide")
st.title("📘 ITRM Platform Instruction Manual")

page_bootstrap(current_page="Help Guide")  # Or "Risk Model", etc.

st.markdown("""
Use this page to read or download the official instruction manual for the ITRM platform. This guide walks through each module in the application and explains how to use the tool to its fullest potential.
""")

# --- 📖 Hardcoded Instruction Content ---
st.subheader("🧩 Module Overview")

st.markdown("""
### 🔹 1. Component Mapping  
Define your IT environment, assign risk and maturity, and link to business impact.  
**Inputs**: Infra components, maturity, risk, criticality  
**Outputs**: Inventory, Spend by Category, Roadmap

### 🔹 2. Executive Dashboard  
Quickly visualize IT spend, risk exposure, and ROI trends.  
**Inputs**: Revenue, IT spend  
**Outputs**: Charts (ITRM, Revenue at Risk), KPIs

### 🔹 3. Forecast & Sensitivity Simulator  
Project spend trends and test budget levers by category.  
**Inputs**: Growth %, spend categories  
**Outputs**: 3-Year Forecast, Sensitivity Table

### 🔹 4. ITRM Financial Calculator  
Run simulations to optimize IT value vs. cost.  
**Inputs**: Baseline & optimized spend  
**Outputs**: ROI, Payback, Savings

### 🔹 5. Architecture Optimization  
Visualize architecture and run optimization suggestions.  
**Inputs**: Visio upload or component list  
**Outputs**: AI Roadmap, Heatmap, Timeline

### 🔹 6. IT Maturity Assessment  
Score maturity by domain using yes/no answers.  
**Inputs**: Assessment responses  
**Outputs**: Maturity scores, action items

### 🔹 7. Cybersecurity Assessment  
Evaluate security across CIS/NIST controls.  
**Inputs**: Yes/No by domain (Protect, Detect, etc.)  
**Outputs**: Cyber Scorecard, Recommendations

### 🔹 8. Strategic Roadmap  
Align projects to business priorities over time.  
**Inputs**: Maturity scores, IT goals  
**Outputs**: Timeline by Quarter, Milestone Checklist

### 🔹 9. Benchmarking  
Compare IT maturity and spend to peers.  
**Inputs**: Industry, org size, persona  
**Outputs**: Persona profiles, peer visuals

### 🔹 10. AI Recommendations  
Use AI to guide decisions or suggest vendors/tools.  
**Inputs**: Natural language questions  
**Outputs**: AI insights, strategy ideas, guidance
""")

# Download button
with open(pdf_path, "rb") as pdf_file:
    st.download_button(
        label="📥 Download ITRM Instruction Manual (PDF)",
        data=pdf_file,
        file_name="ITRM_Instruction_Manual.pdf",
        mime="application/pdf"
    )

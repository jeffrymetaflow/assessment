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
Use this page to read the official instruction manual for the ITRM platform. This guide walks through each module in the application and explains how to use the tool to its fullest potential.
""")

# --- 📖 Hardcoded Instruction Content ---
st.subheader("🧩 Module Overview")

### 🔹 1. IT Maturity Assessment  
Score maturity by domain using yes/no answers.  
**Inputs**: Assessment responses  
**Outputs**: Maturity scores, action items

### 🔹 2. Cybersecurity Assessment  
Evaluate security across CIS/NIST controls.  
**Inputs**: Yes/No by domain (Protect, Detect, etc.)  
**Outputs**: Cyber Scorecard, Recommendations

### 🔹 3. Strategic Roadmap  
Align projects to business priorities over time.  
**Inputs**: Maturity scores, IT goals  
**Outputs**: Timeline by Quarter, Milestone Checklist

### 🔹 4. AI Recommendations  
Use AI to guide decisions or suggest vendors/tools.  
**Inputs**: Natural language questions  
**Outputs**: AI insights, strategy ideas, guidance
""")


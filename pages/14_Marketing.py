import streamlit as st
from utils.auth import enforce_login

# --- Auth ---
enforce_login()

# --- Page Config ---
st.set_page_config(page_title="ITRM Impact Summary", layout="wide")

# --- Header ---
st.title("🚀 Before vs. After ITRM")
st.markdown("See how ITRM transforms IT buyer-seller interactions and strategic outcomes.")

# --- Comparison Columns ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("❌ Before ITRM")
    st.markdown("""
    - Buyers feel pressure, lack business justification  
    - Sellers rely on pitch decks and quota-chasing  
    - Sales Leaders have unpredictable pipelines  
    - Assessments are manual or missing  
    - Financial justification is unclear or untrusted  
    - Cyber, spend, and architecture data are siloed  
    """)

with col2:
    st.subheader("✅ After ITRM")
    st.markdown("""
    - Buyers gain strategic clarity and internal alignment  
    - Sellers become trusted advisors with AI support  
    - Sales Leaders manage smarter, strategic pipelines  
    - Simulators + assessments automate discovery  
    - Financial outcomes modeled in real-time  
    - Unified platform aligns risk, spend, and roadmap  
    """)

# --- Divider ---
st.markdown("---")

# --- Value Proposition ---
st.title("👥 What’s In It for Me?")
cols = st.columns(3)

with cols[0]:
    st.subheader("🎯 For Buyers")
    st.markdown("""
    - Confident IT decision-making  
    - Clear business case for each initiative  
    - Faster internal buy-in and approvals  
    """)

with cols[1]:
    st.subheader("🤝 For Sellers")
    st.markdown("""
    - Faster discovery + shorter cycles  
    - Strategic conversation starters  
    - Real-time financial justification tools  
    """)

with cols[2]:
    st.subheader("📈 For Sales Leaders")
    st.markdown("""
    - Forecastable, aligned pipeline  
    - Repeatable, AI-supported strategy  
    - Better retention and higher close rates  
    """)

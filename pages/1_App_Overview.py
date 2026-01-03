import streamlit as st
from utils.auth import enforce_login

# --- Enforce authentication
enforce_login()

# --- Page config
st.set_page_config(page_title="📘 ITRM Platform Tour", layout="wide")
st.title("📘 Welcome to the ITRM Platform")
st.markdown("Explore the key modules that power Intelligent Technology Risk Management and how to use them effectively.")

# --- Module Guide
with st.expander("🔐 Login & Project Setup"):
    st.markdown("""
- Secure your session with user login  
- Define your project name, client name, and revenue assumptions  
- All data is stored in-session or can be exported to Supabase or JSON  
""")

with st.expander("📊 IT & Cyber Maturity Assessments"):
    st.markdown("""
- Complete structured assessments for IT and Cybersecurity  
- Get maturity scores mapped to CIS, NIST, and strategic domains  
- Results flow into other modules for roadmap and spend modeling  
""")

with st.expander("📅 Strategic Roadmap Builder"):
    st.markdown("""
- Automatically generate a transformation roadmap  
- Prioritize actions by maturity gaps and business impact  
- Align roadmap phases to your IT budget timeline  
""")

with st.expander("🛍️ Product Intelligence + Supplier Matching"):
    st.markdown("""
- See recommended tools and suppliers based on your gaps  
- Score-matched vendors from the Nexus One ecosystem  
- Compare estimated pricing and export to budget scenarios  
""")

with st.expander("🤖 AI Readiness & Recommendations"):
    st.markdown("""
- Assess your AI maturity across infrastructure, data, skills, and ethics  
- Get tailored improvement actions and sample tools  
- Feed results into your strategic roadmap and supplier match  
""")

with st.expander("🧠 AI Assistant Module"):
    st.markdown("""

import streamlit as st
from utils.auth import enforce_login

# Enforce login
enforce_login()

# Page config
st.set_page_config(page_title="📘 ITRM Platform Tour", layout="wide")

# Title and intro
st.title(":blue_book: Welcome to the ITRM Platform")
st.markdown("This guide will walk you through the core modules of the ITRM app and how to use them effectively.")

# Expanders
with st.expander("🔐 Login & Session Setup"):
    st.markdown("""
    - Secure access to protect your session  
    - Set up your project name, client, and revenue  
    - All data is saved to your session or exportable to JSON
    """)

with st.expander("🤖 AI Readiness"):
    st.markdown("""
    - Complete structured assessments  
    - Receive scores across 5 categories  
    - Align long-term IT planning with spend and risk
    """)

with st.expander("🔐 Cybersecurity & IT Maturity"):
    st.markdown("""
    - Complete structured assessments  
    - Receive scores across CIS & NIST controls  
    - Feed results into the dashboard for strategic alignment
    """)

with st.expander("🤡 Strategic Roadmap"):
    st.markdown("""
    - Build a transformation roadmap  
    - Map against industry personas and use cases  
    - Align long-term IT planning with spend and risk
    """)

with st.expander("🤖 AI Assist Module"):
    st.markdown("""
    - Ask questions or request recommendations  
    - AI Advisor uses your project data and context  
    - Supports sellers and IT pros with real-time answers
    """)

# Final message
st.markdown("---")
st.info("You're now ready to begin exploring! Use the sidebar to start your ITRM journey.")

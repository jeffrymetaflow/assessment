import streamlit as st
from utils.auth import enforce_login
enforce_login()

st.set_page_config(page_title="📘 ITRM Platform Tour", layout="wide")

st.title(":blue_book: Welcome to the ITRM Platform")
st.markdown("This guide will walk you through the core modules of the ITRM app and how to use them effectively.")

with st.expander("🔐 Login & Session Setup"):
    st.markdown("""
    - Secure access to protect your session
    - Set up your project name, client, and revenue
    - All data is saved to your session or exportable to JSON
    """)

with st.expander("🧱 Component Mapping"):
    st.markdown("""
    - Upload architecture or describe major components
    - Classify spend by category (HW, SW, Cloud, etc.)
    - This drives cost visuals and architectural AI analysis
    """)

with st.expander("🏩 Architecture + AI"):
    st.markdown("""
    - Upload Visio or describe project structure
    - Run AI analysis on optimization opportunities
    - View potential architecture alternatives
    """)

with st.expander("🔐 Cybersecurity & IT Maturity"):
    st.markdown("""
    - Complete structured assessments
    - Receive scores across CIS & NIST controls
    - Feed results into the dashboard for strategic alignment
    """)

with st.expander("🤡 Strategic Roadmap + Personas"):
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

st.markdown("---")
st.info("You're now ready to begin exploring! Use the sidebar to start your ITRM journey.")



import streamlit as st
from controller.controller import ITRMController

# Initialize the shared controller (only once)
if "controller" not in st.session_state:
    st.session_state.controller = ITRMController()

# Configure the app
st.set_page_config(
    page_title="ITRM Unified App",
    layout="wide"
)

# --- Layout with logo ---
col1, col2 = st.columns([6, 1])  # 6:1 ratio for left vs right

with col1:
    st.title("💡 ITRM Unified Platform")
    st.markdown("""
    Welcome to the **IT Revenue Management (ITRM)** platform.

    Use the sidebar to access modules like:
    - 🧩 Component Mapping
    - 🗺️ Architecture Visualization
    - 📊 Forecast & Risk Simulation
    - 🤖 AI Strategy Assistant

    This tool helps IT leaders align architecture to financial and strategic impact — all in one place.
    """)

with col2:
    st.image("Market image.png", width=200)

import streamlit as st
from utils.ai_assist import ai_assist_overlay

# Inject AI Assistant in the sidebar globally
with st.sidebar.expander("💬 AI Assistant", expanded=False):
    ai_assist_overlay()

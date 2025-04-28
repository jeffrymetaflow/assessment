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

# Inject AI Assistant with full context
from utils.bootstrap import page_bootstrap
page_bootstrap(current_page="Main")

import uuid

# --- Check if project metadata exists ---
if "project_id" not in st.session_state:
    with st.form("new_project_form", clear_on_submit=True):
        st.subheader("🛠️ Start a New Client Assessment")
        client_name = st.text_input("Client Name")
        project_name = st.text_input("Project/Assessment Name")
        submitted = st.form_submit_button("Start Assessment")

        if submitted:
            if client_name and project_name:
                st.session_state["client_name"] = client_name
                st.session_state["project_name"] = project_name
                st.session_state["project_id"] = str(uuid.uuid4())
                st.success(f"Started project: {client_name} - {project_name}")
                st.experimental_rerun()
            else:
                st.error("Please enter both Client and Project names.")
else:
    st.markdown(f"**Client:** {st.session_state['client_name']}  |  **Project:** {st.session_state['project_name']}  |  **Project ID:** {st.session_state['project_id']}")


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



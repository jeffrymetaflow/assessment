import streamlit as st
import os
import json
import uuid
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

# --- Project Save/Load Functions ---
def save_project():
    if not os.path.exists("projects"):
        os.makedirs("projects")
    project_id = st.session_state.get("project_id", str(uuid.uuid4()))
    data = {
        "client_name": st.session_state.get("client_name", ""),
        "project_name": st.session_state.get("project_name", ""),
        "project_id": project_id,
        "components": st.session_state.controller.get_components(),
    }
    filepath = f"projects/{project_id}.json"
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)
    st.success(f"Project saved successfully: {filepath}")

def load_project(project_file):
    filepath = os.path.join("projects", project_file)
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
            st.session_state["client_name"] = data.get("client_name", "")
            st.session_state["project_name"] = data.get("project_name", "")
            st.session_state["project_id"] = data.get("project_id", str(uuid.uuid4()))
            st.session_state.controller.set_components(data.get("components", []))
            st.success(f"Project {st.session_state['project_name']} loaded successfully!")
    else:
        st.error("Selected project file not found.")

# --- Sidebar Save/Load Controls ---
with st.sidebar:
    st.subheader("💾 Project Management")
    
    if "project_id" in st.session_state:
        if st.button("Save Current Project"):
            save_project()

    if os.path.exists("projects"):
        project_files = os.listdir("projects")
        if project_files:
            selected_file = st.selectbox("Load a Saved Project", project_files)
            if st.button("Load Selected Project"):
                load_project(selected_file)

# --- Landing Page: New or Existing Project ---
if "project_id" not in st.session_state:
    st.title("🚀 Welcome to the ITRM Platform")
    st.subheader("Start a New Assessment or Load an Existing One")

    option = st.radio(
        "Choose an option:",
        ("➕ Start New Client Assessment", "📂 Open Existing Project"),
        horizontal=True
    )

    if option == "➕ Start New Client Assessment":
        with st.form("new_project_form", clear_on_submit=True):
            client_name = st.text_input("Client Name")
            project_name = st.text_input("Project/Assessment Name")
            submitted = st.form_submit_button("Start New Project")

            if submitted:
                if client_name and project_name:
                    st.session_state["client_name"] = client_name
                    st.session_state["project_name"] = project_name
                    st.session_state["project_id"] = str(uuid.uuid4())
                    st.success(f"Started project: {client_name} - {project_name}")
                    st.stop()
                else:
                    st.error("Please enter both Client and Project names.")

    elif option == "📂 Open Existing Project":
        if os.path.exists("projects"):
            project_files = os.listdir("projects")
            if project_files:
                selected_file = st.selectbox("Select a saved project to load", project_files)
                if st.button("Load Selected Project"):
                    load_project(selected_file)
                    st.stop()
            else:
                st.warning("No saved projects found. Please create a new assessment first.")
        else:
            st.warning("Project folder does not exist yet.")
else:
    # --- Normal App Flow (Project Active) ---
    col1, col2 = st.columns([6, 1])

    with col1:
        # Display active Client/Project
        with st.expander("📁 Active Project", expanded=True):
            st.markdown(
                f"**Client:** {st.session_state['client_name']}  \n"
                f"**Project:** {st.session_state['project_name']}  \n"
                f"**Project ID:** {st.session_state['project_id']}"
            )

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




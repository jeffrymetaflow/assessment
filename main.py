import streamlit as st
import os
import json
import uuid
from fpdf import FPDF
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

# --- PDF Generation Function with Optional Logo and Risk Table ---
def generate_roadmap_pdf():
    pdf = FPDF()
    pdf.add_page()

    logo_path = "assets/logo.png"
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=160, y=10, w=40)

    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, "ITRM Modernization Roadmap", ln=True, align='C')
    pdf.ln(20)

    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, f"Client: {st.session_state.get('client_name', '')}", ln=True)
    pdf.cell(0, 10, f"Project: {st.session_state.get('project_name', '')}", ln=True)
    pdf.cell(0, 10, f"Project ID: {st.session_state.get('project_id', '')}", ln=True)
    pdf.ln(10)

    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, "Architecture Components:", ln=True)
    pdf.set_font("Helvetica", size=12)

    components = st.session_state.controller.get_components()
    if components:
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(50, 10, "Name", border=1, fill=True)
        pdf.cell(40, 10, "Category", border=1, fill=True)
        pdf.cell(40, 10, "Spend", border=1, fill=True)
        pdf.cell(40, 10, "Renewal Date", border=1, fill=True)
        pdf.ln()

        for comp in components:
            if isinstance(comp, dict):
                name = comp.get('Name', 'Unknown')
                category = comp.get('Category', 'N/A')
                spend = f"${comp.get('Spend', 0):,}"
                renewal = comp.get('Renewal Date', 'TBD')
                pdf.cell(50, 10, name, border=1)
                pdf.cell(40, 10, category, border=1)
                pdf.cell(40, 10, spend, border=1)
                pdf.cell(40, 10, renewal, border=1)
                pdf.ln()
    else:
        pdf.cell(0, 10, "No components found.", ln=True)

    pdf.ln(10)

    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, "Risk Summary + Recommendations:", ln=True)
    pdf.set_font("Helvetica", size=12)

    risk_items = [
        {"Risk": "Aging Server Infrastructure", "Recommendation": "Consider cloud migration for elasticity", "Severity": 5, "Spend Impact": 100000},
        {"Risk": "Legacy Firewall Rules", "Recommendation": "Conduct firewall policy modernization review", "Severity": 3, "Spend Impact": 50000},
        {"Risk": "No DR Plan", "Recommendation": "Design and implement DR/BC solution with cloud failover", "Severity": 4, "Spend Impact": 75000},
    ]

    # Sort risks by (Severity * Spend Impact) descending
    risk_items.sort(key=lambda x: x.get("Severity", 0) * x.get("Spend Impact", 0), reverse=True)

    priority_number = 1
    for item in risk_items:
        pdf.cell(0, 10, f"{priority_number}. Risk: {item['Risk']}", ln=True)
        pdf.cell(0, 10, f"   Action: {item['Recommendation']}", ln=True)
        pdf.cell(0, 10, f"   Severity: {item['Severity']} | Spend Impact: ${item['Spend Impact']:,}", ln=True)
        pdf.ln(5)
        priority_number += 1

    if not os.path.exists("exports"):
        os.makedirs("exports")
    filepath = f"exports/{st.session_state['project_id']}_roadmap.pdf"
    pdf.output(filepath)

    return filepath

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

        # --- Add New Component Form ---
        st.subheader("➕ Add New Architecture Component")

        with st.form("add_component_form", clear_on_submit=True):
            new_component = st.text_input("Component Name")
            submitted = st.form_submit_button("Add Component")

            if submitted:
                if new_component:
                    components = st.session_state.controller.get_components()
                    components.append(new_component)
                    st.session_state.controller.set_components(components)
                    st.success(f"Added component: {new_component}")
                else:
                    st.error("Please enter a component name.")

        if st.button("📄 Generate Modernization Roadmap PDF"):
            pdf_path = generate_roadmap_pdf()
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="📥 Download Roadmap PDF",
                    data=pdf_file,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf"
                )

    with col2:
        st.image("Market image.png", width=200)




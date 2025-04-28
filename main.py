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

# --- Vendor Mapping Template ---
vendor_mapping = {
    "Hardware": ["Dell", "HPE", "Lenovo"],
    "Software": ["Microsoft", "Oracle", "SAP"],
    "Security": ["Palo Alto Networks", "Fortinet", "CrowdStrike"],
    "Networking": ["Cisco", "Juniper", "Arista"],
    "Cloud": ["AWS", "Azure", "Google Cloud"],
    "Storage": ["Pure Storage", "NetApp", "Dell EMC"]
}

# --- Dynamic AI Modernization Suggestion Function ---
def dynamic_generate_modernization_suggestion(category, spend, renewal_date, risk_score):
    suggestion = ""

    if category in ["Hardware", "Storage"] and spend > 100000:
        suggestion += "Explore cloud migration to reduce capex and enhance scalability. "
    if category == "Software" and risk_score > 7:
        suggestion += "Evaluate SaaS alternatives to improve security and upgrade cycles. "
    if category == "Networking" and renewal_date:
        suggestion += "Modernize network with SD-WAN or next-gen architecture solutions. "
    if category == "Security" and risk_score > 8:
        suggestion += "Implement zero-trust security models with AI-driven threat detection. "
    if category == "Cloud" and spend > 50000:
        suggestion += "Optimize multi-cloud deployments for cost savings and resiliency. "

    if not suggestion:
        suggestion = "Review current asset lifecycle and evaluate modernization opportunities based on strategic goals."

    return suggestion

# --- Spend Savings Estimation Function ---
def generate_spend_saving_estimate(category, spend, modernization_action):
    if "cloud" in modernization_action.lower():
        savings = spend * 0.25
        return f"Estimated Savings: ~${int(savings):,} over 3 years"
    if "saas" in modernization_action.lower():
        savings = spend * 0.15
        return f"Estimated Operational Savings: ~${int(savings):,}"
    if "sd-wan" in modernization_action.lower():
        savings = spend * 0.10
        return f"Network Optimization Savings: ~${int(savings):,}"
    return "Savings Estimate: N/A"

# --- PDF Generation Function with Timeline Staging ---
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
        pdf.cell(40, 10, "Name", border=1, fill=True)
        pdf.cell(30, 10, "Category", border=1, fill=True)
        pdf.cell(30, 10, "Spend", border=1, fill=True)
        pdf.cell(40, 10, "Renewal Date", border=1, fill=True)
        pdf.cell(50, 10, "Suggested Vendors", border=1, fill=True)
        pdf.ln()

        for comp in components:
            if isinstance(comp, dict):
                name = comp.get('Name', 'Unknown')
                category = comp.get('Category', 'N/A')
                spend_val = comp.get('Spend', 0)
                spend = f"${spend_val:,}"
                renewal = comp.get('Renewal Date', 'TBD')
                suggested_vendors = ", ".join(vendor_mapping.get(category, ["TBD"]))
                risk_score = comp.get('Risk Score', 5)
                pdf.cell(40, 10, name, border=1)
                pdf.cell(30, 10, category, border=1)
                pdf.cell(30, 10, spend, border=1)
                pdf.cell(40, 10, renewal, border=1)
                pdf.cell(50, 10, suggested_vendors, border=1)
                pdf.ln()

                modernization = dynamic_generate_modernization_suggestion(category, spend_val, renewal, risk_score)
                savings = generate_spend_saving_estimate(category, spend_val, modernization)
                pdf.cell(0, 10, f"   -> Modernization Suggestion: {modernization}", ln=True)
                pdf.cell(0, 10, f"   -> {savings}", ln=True)
                pdf.ln(2)
    else:
        pdf.cell(0, 10, "No components found.", ln=True)

    pdf.ln(10)

    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, "Modernization Timeline:", ln=True)
    pdf.set_font("Helvetica", size=12)

    risk_items = [
        {"Risk": "Aging Server Infrastructure", "Recommendation": "Consider cloud migration for elasticity", "Severity": 5, "Spend Impact": 100000, "Target Year": 2025},
        {"Risk": "Legacy Firewall Rules", "Recommendation": "Conduct firewall policy modernization review", "Severity": 3, "Spend Impact": 50000, "Target Year": 2026},
        {"Risk": "No DR Plan", "Recommendation": "Design and implement DR/BC solution with cloud failover", "Severity": 4, "Spend Impact": 75000, "Target Year": 2025},
    ]

    risk_items.sort(key=lambda x: (x.get("Target Year", 2025), -(x.get("Severity", 0) * x.get("Spend Impact", 0))))

    current_year = None
    priority_number = 1
    for item in risk_items:
        if item.get("Target Year") != current_year:
            current_year = item.get("Target Year")
            pdf.ln(5)
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 10, f"{current_year}", ln=True)
            pdf.set_font("Helvetica", size=12)

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




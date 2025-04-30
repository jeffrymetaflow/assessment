import streamlit as st
import os
import json
import uuid
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
from controller.controller import ITRMController
from utils.bootstrap import page_bootstrap

# ✅ MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(page_title="ITRM Main Dashboard", layout="wide")

# --- INIT CONTROLLER ---
if "controller" not in st.session_state:
    st.session_state.controller = ITRMController()

controller = st.session_state.controller

# --- USER JOURNEY ---
st.title("🚀 Welcome to the ITRM Platform")
st.subheader("Start a New Assessment or Load an Existing One")

step = st.radio("Select Option:", ["➕ Start New Client Assessment", "📂 Open Existing Project"], horizontal=True)

if step == "➕ Start New Client Assessment":
    with st.form("new_project_form", clear_on_submit=True):
        client_name = st.text_input("Client Name")
        project_name = st.text_input("Project / Assessment Name")
        submitted = st.form_submit_button("Start New Project")

        if submitted:
            if client_name and project_name:
                st.session_state["client_name"] = client_name
                st.session_state["project_name"] = project_name
                st.session_state["project_id"] = str(uuid.uuid4())
                st.rerun()
            else:
                st.error("Please fill in both fields.")

elif step == "📂 Open Existing Project":
    st.warning("Project loader functionality coming soon.")

# --- PROJECT ACTIVE FLOW ---
if "project_id" in st.session_state:
    st.success(f"📁 Active Project: {st.session_state['client_name']} | {st.session_state['project_name']}")

    # --- REVENUE SETUP ---
    with st.expander("💵 Project Revenue", expanded=True):
        if "project_revenue" not in st.session_state:
            st.session_state["project_revenue"] = ""
    
        st.markdown("## 💵 Project Revenue")
        st.caption("Enter the annual revenue this IT architecture supports. You can type it manually or click auto-fetch:")
        
        st.text_input("Annual Revenue (USD)", key="project_revenue")
        
        if st.session_state.get("client_name"):
            revenue_button_label = f"🔍 Try Auto-Fetch for “{st.session_state['client_name']}”"
        else:
            revenue_button_label = "🔍 Try Auto-Fetch (Enter company name first)"
        fetch_button = st.button(revenue_button_label, key="revenue_fetch_button")
        
        st.caption("Hint: Use a publicly traded company name (e.g., 'Cisco', 'Salesforce') for best results.")
       
        if fetch_button:
            try:
                import requests
                from bs4 import BeautifulSoup
    
                client_name = st.session_state.get ("client_name", "")
                if not client_name: 
                    st.warning ("Client name is not set. Please enter a client name first.")
                    st.stop ()
                
                query = f"{client_name} annual revenue site:craft.co"
                url = f"https://www.google.com/search?q={query}"
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")
                text = soup.get_text()
    
                import re
                match = re.search(r"\$[\d,]+[MBT]?", text)
                if match:
                    st.session_state["project_revenue"] = match.group(0)
                    st.success(f"Auto-fetched estimated revenue: {match.group(0)}")
                else:
                    st.warning("Could not extract revenue. Please enter it manually.")
    
            except Exception as e:
                st.warning(f"Error fetching revenue: {e}")
    
    # --- COMPONENT UPLOAD ---
    st.markdown("### 📥 Upload Components")
    file = st.file_uploader("Upload .csv with: Name, Category, Spend, Renewal Date, Risk Score")
    if file:
        df = pd.read_csv(file)
        required_cols = {"Name", "Category", "Spend", "Renewal Date", "Risk Score"}
        if required_cols.issubset(set(df.columns)):
            controller.set_components(df.to_dict(orient="records"))
            st.success("✅ Components loaded.")
        else:
            st.error(f"Missing columns: {required_cols - set(df.columns)}")

    # --- COMPONENT PREVIEW ---
    comps = controller.get_components()
    if comps:
        st.markdown("### 🧩 Components Overview")
        st.dataframe(pd.DataFrame(comps))

    # --- SESSION REVENUE IMPACTS ---
    if "revenue_impact_by_category" not in st.session_state:
        st.session_state.revenue_impact_by_category = {
            "Hardware": 10, "Software": 10, "Personnel": 10, "Maintenance": 10,
            "Telecom": 10, "Cybersecurity": 10, "BC/DR": 10, "Compliance": 10, "Networking": 10
        }

    # --- AI Assistant Setup ---
    page_bootstrap(current_page="Main")

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

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 📊 Session Info")
    st.write(f"Client: {st.session_state.get('client_name', '-')}")
    st.write(f"Project: {st.session_state.get('project_name', '-')}")
    st.write(f"Revenue: {st.session_state.get('project_revenue', '-')}")



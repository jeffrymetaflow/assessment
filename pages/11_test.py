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
    st.markdown("### 💵 Project Revenue")
    revenue_input = st.text_input("Enter Revenue ($)", key="project_revenue")
    if revenue_input:
        cleaned = revenue_input.replace("$", "").replace(",", "")
        try:
            st.session_state.baseline_revenue = float(cleaned)
        except:
            st.warning("Invalid revenue format.")

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

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 📊 Session Info")
    st.write(f"Client: {st.session_state.get('client_name', '-')}")
    st.write(f"Project: {st.session_state.get('project_name', '-')}")
    st.write(f"Revenue: {st.session_state.get('project_revenue', '-')}")



import streamlit as st
import os
import json
import uuid
import pandas as pd
import matplotlib.pyplot as plt
import openai
from io import BytesIO
from fpdf import FPDF
from controller.controller import ITRMController
from utils.bootstrap import page_bootstrap
from utils.edgar_utils import fetch_revenue_from_edgar
from utils.session_state import initialize_session
initialize_session()
from utils.auth import enforce_login
enforce_login()
from controller.supabase_controller import get_projects_by_email

# ✅ MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(page_title="ITRM Main Dashboard", layout="wide")

import streamlit as st
from PIL import Image

logo_url = "https://raw.githubusercontent.com/jeffrymetaflow/ITRM-Prototype-v2/main/ITRM%20Logo.png"

st.markdown(
    f"""
    <div style='background-color:#f5f5f5; padding:10px 20px; border-bottom:1px solid #ccc; display:flex; align-items:center; justify-content:space-between;'>
        <img src='{logo_url}' style='height:40px;' alt='Logo'>
        <h4 style='margin:0; color:#333;'>IT Strategy. Business Impact. Real-Time.</h4>
    </div>
    """, unsafe_allow_html=True
)

if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    st.title("👋 Welcome to the ITRM Platform")

    st.markdown("""
    The **IT Revenue Margin (ITRM)** Platform helps align IT operations with strategic business value.  
    ITRM is an AI driven strategic tool for IT professionals & sellers
    
    Before we begin, here’s what you’ll get:

    - AI-generated recommendations to reduce IT Revenue Margin
    - Assessments for optimization/pipeline developent
    - Roadmaps for strategic planning of campaigns

    > Click below to begin your journey.
    """)

    if st.button("🚀 Start Session"):
        st.session_state.started = True
        st.rerun()
    st.stop()

# --- INIT CONTROLLER ---
if "controller" not in st.session_state:
    st.session_state.controller = ITRMController()

if "project_data" not in st.session_state:
    email = "jeff@example.com"
    projects = get_projects_by_email(email)
    if projects:
        project = projects[0]  # Later allow selection
        st.session_state["project_data"] = project

        # Optional: break out fields for convenience
        st.session_state["revenue"] = project["revenue"]
        st.session_state["expenses"] = project["expenses"]
        st.session_state["architecture"] = project["architecture"]
        st.session_state["maturity_score"] = project["maturity_score"]

controller = st.session_state.controller

# --- USER JOURNEY ---
st.title("🚀 Welcome to the ITRM Platform")
st.subheader("Start a New Assessment or Load an Existing One")

step = st.radio("Select Option:", ["➕ Start New Client Assessment", "📂 Open Existing Project"], horizontal=True)

if step == "➕ Start New Client Assessment":
    with st.form("new_project_form", clear_on_submit=True):
        client_name = st.text_input("Client Name")
        project_name = st.text_input("Project / Assessment Name")
        user_email = st.text_input("Your Email Address")  # ← added

        submitted = st.form_submit_button("Start New Project")

        if submitted:
            if client_name and project_name and user_email:
                st.session_state["client_name"] = client_name
                st.session_state["project_name"] = project_name
                st.session_state["user_email"] = user_email

                # Create initial project_data payload
                st.session_state["project_data"] = {
                    "user_email": user_email,
                    "project_name": project_name,
                    "maturity_score": 0
                }

                # Also store individual fields for easier access in pages
                st.session_state["revenue"] = 0
                st.session_state["expenses"] = {}
                st.session_state["architecture"] = {}
                st.session_state["maturity_score"] = 0

                st.success("🧾 New project session created. Navigate to any tab to begin.")
                st.rerun()
            else:
                st.error("Please fill in all fields including email.")

elif step == "📂 Open Existing Project":
    st.subheader("📂 Load an Existing Project")

    from controller.supabase_controller import get_projects_by_email

    email = st.text_input("Enter your email address to load saved projects")

    if email:
        projects = get_projects_by_email(email)

        if projects:
            selected = st.selectbox("Select a project:", [p["project_name"] for p in projects])
            project = next(p for p in projects if p["project_name"] == selected)

            # Load into session_state
            st.session_state["project_data"] = project
            st.session_state["maturity_score"] = project.get("maturity_score")

            st.success(f"✅ Project '{project['project_name']}' loaded. Navigate to any tab to begin.")
        else:
            st.warning("No projects found for this email.")

        from controller.supabase_controller import delete_project_by_id

        if st.button("🗑️ Delete This Project"):
            confirm = st.checkbox("Confirm deletion of this project")
        
            if confirm:
                result = delete_project_by_id(project["id"])
                if result:
                    st.success("🗑️ Project successfully deleted.")
        
                    # Clear session to avoid stale data
                    for key in ["project_data", "maturity_score"]:
                        st.session_state.pop(key, None)
                    st.rerun()

# --- USER AUTHENTICATION CHECK ---
if "user_email" not in st.session_state:
    st.warning("Please login to continue.")
    st.stop()

# --- PROJECT SELECTION ---
if "project_data" not in st.session_state:
    st.info("No active project. Please start a new assessment or load an existing project.")
        # --- PROJECT START/OPEN OPTIONS ---
    step = st.radio("Select Option:", ["➕ Start New Client Assessment", "📂 Open Existing Project"], horizontal=True)

    if step == "➕ Start New Client Assessment":
        with st.form("new_project_form", clear_on_submit=True):
            client_name = st.text_input("Client Name")
            project_name = st.text_input("Project / Assessment Name")
            user_email = st.session_state.get("user_email", "")  # pre-populate from session

            submitted = st.form_submit_button("Start New Project")

            if submitted:
                if client_name and project_name and user_email:
                    st.session_state["client_name"] = client_name
                    st.session_state["project_name"] = project_name
                    import uuid

                    project_id = str(uuid.uuid4())
                    st.session_state["project_data"] = {
                        "id": project_id,
                        "client_name": client_name,
                        "project_name": project_name
                    }
                    st.success("New project created successfully. Please continue below.")
                else:
                    st.warning("Please complete all fields to start a new project.")

    elif step == "📂 Open Existing Project":
        st.info("(Placeholder) Load existing projects from your storage/database here.")
else:
    # --- PROJECT ACTIVE INFO ---
    st.success(f"📁 Active Project: {st.session_state.get('client_name', 'Unknown Client')} | {st.session_state.get('project_name', 'Unknown Project')}")
    
    # --- AI Assistant Setup ---
    page_bootstrap(current_page="Main")

   
    # --- Reset Project State ---
    if st.button("Start New Project"):
        if "controller" in st.session_state and hasattr(st.session_state.controller, "clear_components"):
            st.session_state.controller.clear_components()
        else:
            st.error("Controller is not initialized or does not have the 'clear_components' method.")
            st.session_state["csv_loaded"] = False
            st.session_state["json_loaded"] = False
            st.session_state["pdf_loaded"] = False
            st.session_state["visio_loaded"] = False
              

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 📊 Session Info")
    st.write(f"Client: {st.session_state.get('client_name', '-')}")
    st.write(f"Project: {st.session_state.get('project_name', '-')}")

# Export session as downloadable JSON
session_data = {k: v for k, v in st.session_state.items() if not k.startswith('_')}
json_str = json.dumps(session_data, default=str)
st.sidebar.download_button(
    label="💾 Export Session",
    data=json_str,
    file_name="ITRM-session.json",
    mime="application/json"
)

# Upload session to restore state
uploaded_file = st.sidebar.file_uploader("🔁 Import Session", type="json")
if uploaded_file is not None:
    uploaded_state = json.load(uploaded_file)
    for k, v in uploaded_state.items():
        st.session_state[k] = v
    st.sidebar.success("✅ Session loaded!")

if st.sidebar.button("🧹 Reset Session"):
    reserved_keys = {"_is_running_with_streamlit", "rerun_data", "_session_state"}
    for key in list(st.session_state.keys()):
        if key not in reserved_keys:
            del st.session_state[key]

    st.experimental_rerun()

# --- AI Assistant Reasoning Enhancement ---
def assist_modernization_reasoning(name, category, spend, renewal_date, risk_score):
    modernization = dynamic_generate_modernization_suggestion(category, spend, renewal_date, risk_score)
    savings = generate_spend_saving_estimate(category, spend, modernization)
    avg_market_spend = simulate_external_pricing_lookup(category)
    variance = ((spend - avg_market_spend) / avg_market_spend) * 100 if avg_market_spend else 0
    aws_cloud_cost = simulate_aws_cloud_pricing(category, spend)
    cloud_savings = spend - aws_cloud_cost

    reasoning = f"""
Component: {name}
Category: {category}
Spend: ${spend:,}
Renewal Date: {renewal_date}
Risk Score: {risk_score}/10
Industry Average Spend: ~${avg_market_spend:,}
Variance vs Market: {variance:+.1f}%
AWS Cloud Alternative: ~${aws_cloud_cost:,}
Potential Cloud Migration Savings: ~${cloud_savings:,}

Modernization Recommendation: {modernization}
{savings}

Reasoning: Based on high spend, risk profile, renewal timing, variance against market average, and potential cloud migration savings, modernization is prioritized to optimize cost, performance, security, and compliance.
"""
    return reasoning

st.markdown(
    "📄 By using this prototype, you agree to our [Terms](#) and [Privacy Notice](#). "
    "This tool is for pilot use only and does not represent final security controls.",
    unsafe_allow_html=True
)


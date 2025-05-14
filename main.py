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
from controller.supabase_controller import get_projects_by_email, save_project

# ✅ MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(page_title="ITRM Main Dashboard", layout="wide")

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
if st.session_state.get("new_project_created"):
    st.session_state.pop("new_project_created", None)
    st.experimental_rerun()

if "controller" not in st.session_state:
    st.session_state.controller = ITRMController()

if "project_data" not in st.session_state:
    email = "jeff@example.com"
    projects = get_projects_by_email(email)
    if projects:
        project = projects[0]  # Later allow selection
        st.session_state["project_data"] = project
        st.session_state["maturity_score"] = project.get("maturity_score", 0)

controller = st.session_state.controller

# --- USER JOURNEY ---
st.title("🚀 Welcome to the ITRM Platform")
st.subheader("Start a New Assessment or Load an Existing One")

step = st.radio("Select Option:", ["➕ Start New Client Assessment", "📂 Open Existing Project"], horizontal=True)

if step == "➕ Start New Client Assessment":
    with st.form("new_project_form", clear_on_submit=True):
        client_name = st.text_input("Client Name")
        project_name = st.text_input("Project / Assessment Name")
        user_email = st.text_input("Your Email Address")

        submitted = st.form_submit_button("Start New Project")

        if submitted:
            if client_name and project_name and user_email:
                project_id = str(uuid.uuid4())
                project_payload = {
                    "project_id": project_id,
                    "client_name": client_name,
                    "project_name": project_name,
                    "user_email": user_email,
                    "session_data": {}
                }
                result = save_project(project_payload)

                if result:
                    st.session_state["project_data"] = result
                    st.session_state["client_name"] = client_name
                    st.session_state["project_name"] = project_name
                    st.session_state["user_email"] = user_email
                    st.session_state["new_project_created"] = True

                    st.success("New project created and saved to Supabase. Please proceed.")
                else:
                    st.error("Failed to save project. Please try again.")
            else:
                st.error("Please fill in all fields including email.")



elif step == "📂 Open Existing Project":
    st.subheader("📂 Load an Existing Project")

    email = st.text_input("Enter your email address to load saved projects")

    if email:
        projects = get_projects_by_email(email)

        if projects:
            selected = st.selectbox("Select a project:", [p["project_name"] for p in projects])
            project = next(p for p in projects if p["project_name"] == selected)

            st.session_state["project_data"] = project
            if "session_data" in project:
                session_data = project["session_data"]
                st.session_state["maturity_score"] = session_data.get("maturity_score")
                st.session_state["it_maturity_answers"] = session_data.get("maturity_answers")
                st.session_state["cybersecurity_answers"] = session_data.get("cyber_answers")
                st.success("🔄 Project session data synced.")
            else:
                st.warning("⚠️ No session data found for this project.")

# --- USER AUTHENTICATION CHECK ---
if "user_email" not in st.session_state:
    st.warning("Please login to continue.")
    st.stop()

# --- PROJECT SELECTION ---
if "project_data" not in st.session_state:
    st.info("No active project. Please start a new assessment or load an existing project.")
else:
    st.success(f"📁 Active Project: {st.session_state.get('client_name', 'Unknown Client')} | {st.session_state.get('project_name', 'Unknown Project')}")
    page_bootstrap(current_page="Main")

    if st.button("Start New Project"):
        if "controller" in st.session_state and hasattr(st.session_state.controller, "clear_components"):
            st.session_state.controller.clear_components()
        else:
            st.error("Controller is not initialized or does not have the 'clear_components' method.")
        st.session_state.clear()
        st.experimental_rerun()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 📊 Session Info")
    st.write(f"Client: {st.session_state.get('client_name', '-')}")
    st.write(f"Project: {st.session_state.get('project_name', '-')}")

session_data = {k: v for k, v in st.session_state.items() if not k.startswith('_')}
json_str = json.dumps(session_data, default=str)
st.sidebar.download_button(
    label="💾 Export Session",
    data=json_str,
    file_name="ITRM-session.json",
    mime="application/json"
)

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

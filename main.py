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
from utils.session_state import initialize_session
initialize_session()

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
    - Financial justification for strategic decisions 
    - A visualized breakdown of spend vs value, risk, and optimization 
    - Simulation models for what-if scenarios
    - Assessments for optimization/pipeline developent
    - Roadmaps for strategic planning of campaigns
    - Technical modules for architecture decisions/optimization

    > Click below to begin your journey.
    """)

    if st.button("🚀 Start Assessment"):
        st.session_state.started = True
        st.experimental_rerun()
        st.stop()

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
        st.markdown("## 💵 Project Revenue")
        st.caption("Enter the annual revenue this IT architecture supports. You can type it manually or click auto-fetch:")
    
        revenue_input = st.text_input("Annual Revenue (USD)", key="project_revenue")
    
        # 🧠 Sync to global 'revenue' state
        if revenue_input:
            try:
                numeric_revenue = float(revenue_input.replace(",", "").replace("$", ""))
                st.session_state["revenue"] = numeric_revenue
            except:
                st.warning("⚠️ Please enter a valid numeric revenue amount.")

    # Auto-fetch button
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

    # --- JSON Upload Protection ---
    if "json_loaded" not in st.session_state:
        st.session_state["json_loaded"] = False
    
    uploaded_json = st.file_uploader("Upload JSON", type=["json"])
    if uploaded_json and not st.session_state["json_loaded"]:
        if st.button("📥 Load JSON into Project"):
            import json
            data = json.load(uploaded_json)
            if isinstance(data, list):
                df = pd.DataFrame(data)
                if validate_table(df):
                    st.session_state.controller.set_components(df.to_dict(orient="records"))
                    st.session_state["json_loaded"] = True
                    st.success("✅ JSON components loaded successfully.")
    
    # --- PDF Upload Parsing ---
    if "pdf_loaded" not in st.session_state:
        st.session_state["pdf_loaded"] = False
    
    uploaded_pdf = st.file_uploader("Upload PDF (basic table parse)", type=["pdf"])
    if uploaded_pdf and not st.session_state["pdf_loaded"]:
        if st.button("📥 Extract Table from PDF"):
            import pdfplumber
            with pdfplumber.open(uploaded_pdf) as pdf:
                extracted_rows = []
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            if row and any(row):
                                extracted_rows.append(row)
            if extracted_rows:
                extracted_df = pd.DataFrame(extracted_rows)
                if validate_table(extracted_df):
                    extracted_df.columns = REQUIRED_COLUMNS
                    st.session_state.controller.set_components(extracted_df.to_dict(orient="records"))
                    st.session_state["pdf_loaded"] = True
                    st.success("✅ PDF tables extracted and loaded.")
    
                    # Display PDF-parsed components in safe layout
                    st.subheader("📄 Parsed PDF Component Preview")
                    with st.container():
                        for i, comp in enumerate(st.session_state.controller.get_components()):
                            st.markdown(f"**Component {i+1}**")
                            st.markdown(f"- **Name:** {comp.get('Name', 'Unknown')}")
                            st.markdown(f"- **Risk Score:** {comp.get('Risk Score', 'N/A')}")
                            st.markdown(f"- **Category:** {comp.get('Category', 'Unknown')}")
                            st.markdown(f"- **Spend:** ${comp.get('Spend', 0):,}")
                            st.markdown(f"- **Renewal Date:** {comp.get('Renewal Date', 'Unknown')}")
                            st.markdown("---")
            else:
                st.warning("⚠️ No tables found in PDF.")
    
    # --- Visio Upload Parsing ---
    if "visio_loaded" not in st.session_state:
        st.session_state["visio_loaded"] = False
    
    uploaded_visio = st.file_uploader("Upload Visio Diagram (simple metadata parse)", type=["vsdx"])
    if uploaded_visio and not st.session_state["visio_loaded"]:
        if st.button("📥 Parse Visio"):
            from vsdx import VisioFile
            vis = VisioFile(uploaded_visio)
            extracted_shapes = []
            for page in vis.pages:
                for shape in page.shapes:
                    shape_text = shape.text if shape.text else "Unnamed"
                    extracted_shapes.append({"Name": shape_text, "Category": "Unknown", "Spend": 0, "Renewal Date": "", "Risk Score": 5})
            if extracted_shapes:
                df = pd.DataFrame(extracted_shapes)
                if validate_table(df):
                    st.session_state.controller.set_components(df.to_dict(orient="records"))
                    st.session_state["visio_loaded"] = True
                    st.success("✅ Visio diagram shapes parsed and loaded.")
            else:
                st.warning("⚠️ No shapes found in Visio file.")
    
    # --- Display Parsed Components Safely ---
    if st.session_state.get("controller") and st.session_state.controller.get_components():
        with st.expander("📋 View Uploaded Components Overview", expanded=False):
            for i, comp in enumerate(st.session_state.controller.get_components()):
                st.markdown(f"**Component {i+1}**")
                st.markdown(f"- **Name:** {comp.get('Name', 'Unknown')}")
                st.markdown(f"- **Risk Score:** {comp.get('Risk Score', 'N/A')}")
                st.markdown(f"- **Category:** {comp.get('Category', 'Unknown')}")
                st.markdown(f"- **Spend:** ${comp.get('Spend', 0):,}")
                st.markdown(f"- **Renewal Date:** {comp.get('Renewal Date', 'Unknown')}")
                st.markdown("---")
    
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
              
    # --- AIOps / CMDB Mock Connector ---
    st.header("🔌 Connect to AIOps / CMDB System")
    
    if st.button("🌐 Fetch Architecture from AIOps API"):
        simulated_api_response = [
            {"Name": "Web Load Balancer", "Category": "Networking", "Spend": 80000, "Renewal Date": "2025-11-01", "Risk Score": 6},
            {"Name": "Customer Database", "Category": "Storage", "Spend": 200000, "Renewal Date": "2026-03-15", "Risk Score": 8},
            {"Name": "Authentication Server", "Category": "Security", "Spend": 70000, "Renewal Date": "2025-08-30", "Risk Score": 7}
        ]
        st.session_state.aiops_components = simulated_api_response
        st.success("Successfully fetched architecture components from AIOps!")
    
    if 'aiops_components' in st.session_state:
        st.subheader("🔎 AIOps Components Preview")
        for comp in st.session_state.aiops_components:
            st.write(f"- {comp['Name']} ({comp['Category']}) | Spend: ${comp['Spend']:,} | Risk: {comp['Risk Score']}")
    
        if st.button("➕ Import AIOps Components into Architecture"):
            for comp in st.session_state.aiops_components:
                st.session_state.controller.add_component(comp)
            st.success("AIOps components successfully imported into architecture!")
            del st.session_state.aiops_components

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 📊 Session Info")
    st.write(f"Client: {st.session_state.get('client_name', '-')}")
    st.write(f"Project: {st.session_state.get('project_name', '-')}")
    st.write(f"Revenue: {st.session_state.get('project_revenue', '-')}")

# Export session as downloadable JSON
session_data = {k: v for k, v in st.session_state.items() if not k.startswith('_')}
json_str = json.dumps(session_data)
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
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()

# --- Polished AIOps-Specific Risk Insights Dashboard ---
if st.session_state.controller.get_components():
    revenue_display = st.session_state.get("project_revenue", "Not set")
    st.subheader(f"🚨 AIOps Risk Insights Dashboard  |  💰 Revenue: {revenue_display}")

    with st.expander("🚨 View AIOps Risk Insights Dashboard", expanded=True):
        components_df = pd.DataFrame(st.session_state.controller.get_components())
        components_df['Renewal Date'] = pd.to_datetime(components_df['Renewal Date'], errors='coerce')
        expiring_soon = components_df[components_df['Renewal Date'] <= pd.to_datetime('2026-06-30')]
        high_risk = components_df[components_df['Risk Score'] >= 7]

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Components", len(components_df))
        col2.metric("Contracts Expiring by Mid-2026", len(expiring_soon))
        col3.metric("High Risk Components", len(high_risk))

        st.markdown("---")
        tab1, tab2, tab3 = st.tabs(["🛑 Expiring Contracts", "🔥 High Risk Components", "🛠️ Risk Delta Simulation"])

        with tab1:
            if not expiring_soon.empty:
                for comp in expiring_soon.to_dict(orient="records"):
                    name = comp.get('Name', 'Unnamed Component')  # Ensure valid fallback for 'Name'
                    risk_score = comp.get('Risk Score', 'N/A')   # Ensure valid fallback for 'Risk Score'
                    with st.container():
                        st.markdown(f"**Component {i+1}**")
                        st.markdown(f"- **Name:** {comp.get('Name', 'Unknown')}")
                        st.markdown(f"- **Risk Score:** {comp.get('Risk Score', 'N/A')}")
                        st.markdown(f"- **Category:** {comp.get('Category', 'Unknown')}")
                        st.markdown(f"- **Spend:** ${comp.get('Spend', 0):,}")
                        st.markdown(f"- **Renewal Date:** {comp.get('Renewal Date', 'Unknown')}")
                        st.markdown("---")
            else:
                st.info("✅ No contracts expiring soon.") 

        with tab2:
            if not high_risk.empty:
                for i, comp in enumerate(high_risk.to_dict(orient='records')):
                    with st.container():  # Use st.container instead of st.expander
                        st.markdown(f"### {comp['Name']} | Risk Score: {comp['Risk Score']}")  # Display the title
                        st.markdown(f"**Category:** {comp['Category']}")
                        st.markdown(f"**Spend:** ${comp['Spend']:,}")
                        st.markdown(f"**Renewal Date:** {comp['Renewal Date'].date() if pd.notnull(comp['Renewal Date']) else 'N/A'}")
                    
                        # Add the button inside the container
                        if st.button(f"Ask AI Why ({comp['Name']})", key=f"ai_why_{i}"):
                            st.info("🧠 AI Reasoning for this component will appear here...")

            else:
                st.info("✅ No high-risk components identified.")

        with tab3:
            st.subheader("🔧 Simulate Risk Score After Modernization")
            selected_component = st.selectbox("Select a component to simulate:", components_df['Name'].unique())

            if selected_component:
                original_score = components_df.loc[components_df['Name'] == selected_component, 'Risk Score'].values[0]
                st.write(f"Original Risk Score: {original_score}")

                simulated_delta = st.slider("Simulated Risk Improvement (%)", min_value=0, max_value=100, value=20, step=5)
                simulated_new_score = max(0, original_score * (1 - simulated_delta / 100))

                st.metric("Projected New Risk Score", round(simulated_new_score, 1))

                if st.button("💾 Save Simulated New Risk Score"):
                    for i, comp in enumerate(st.session_state.controller.get_components()):
                        if comp['Name'] == selected_component:
                            st.session_state.controller.components[i]['Risk Score'] = round(simulated_new_score, 1)
                            break
                    st.success(f"Updated {selected_component}'s risk score to {round(simulated_new_score, 1)}.")

            if st.button("♻️ Reset All Simulated Risk Scores"):
                for i, comp in enumerate(st.session_state.controller.get_components()):
                    if 'Original Risk Score' in comp:
                        st.session_state.controller.components[i]['Risk Score'] = comp['Original Risk Score']
                    else:
                        st.session_state.controller.components[i]['Risk Score'] = 8
                        st.success("All risk scores reset to default values!")
        
 # --- Executive Summary Calculation Function ---
def generate_executive_summary(components):
    total_spend = 0
    total_cloud_spend = 0
    category_counts = {}
    high_risk_items = []

    for comp in components:
        spend = comp.get("Spend", 0)
        risk = comp.get("Risk Score", 0)
        category = comp.get("Category", "Other")

        total_spend += spend
        cloud_cost = simulate_aws_cloud_pricing(category, spend)
        total_cloud_spend += cloud_cost

        if category not in category_counts:
            category_counts[category] = 0
        category_counts[category] += 1

        high_risk_items.append((comp.get("Name", "Unnamed"), category, spend, risk))

    high_risk_items.sort(key=lambda x: (-x[3], -x[2]))

    return total_spend, total_cloud_spend, category_counts, high_risk_items[:5]

# --- Simulated External Pricing Lookup ---
def simulate_external_pricing_lookup(category):
    market_pricing = {
        "Hardware": 300000,
        "Software": 150000,
        "Security": 100000,
        "Networking": 120000,
        "Cloud": 80000,
        "Storage": 200000,
        "Cybersecurity": 120000,
        "BC/DR": 100000,
        "Compliance": 90000
    }
    return market_pricing.get(category, 100000)

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

# --- Simulated AWS Service Pricing Lookup ---
def simulate_aws_service_pricing(service_name):
    service_pricing = {
        "EC2": 100,
        "S3": 20,
        "RDS": 50,
        "ECS": 30,
        "EFS": 25
    }
    return service_pricing.get(service_name, 75)

# --- Simulated AWS Cloud Pricing Lookup ---
def simulate_aws_cloud_pricing(category, spend):
    discount_mapping = {
        "Hardware": 0.6,
        "Software": 0.8,
        "Security": 0.95,
        "Networking": 0.7,
        "Cloud": 0.9,
        "Storage": 0.5
    }
    discount = discount_mapping.get(category, 0.8)
    return int(spend * discount)

# --- Vendor mapping for PDF usage ---
# Define vendor_mapping globally
vendor_mapping = {
    "Hardware": ["Vendor A", "Vendor B"],
    "Software": ["Vendor C", "Vendor D"],
    "Networking": ["Vendor E"],
    "Cloud": ["Vendor F"],
    # Add other mappings as needed
}

def assist_modernization_reasoning(name, category, spend, renewal_date, risk_score):
    # Check if a suggestion is already cached
    if "modernization_suggestions" not in st.session_state:
        st.session_state["modernization_suggestions"] = {}

    if name in st.session_state["modernization_suggestions"]:
        modernization = st.session_state["modernization_suggestions"][name]
    else:
        # Call AI to generate a suggestion
        modernization = dynamic_generate_modernization_suggestion(category, spend, renewal_date, risk_score)
        st.session_state["modernization_suggestions"][name] = modernization

    # Generate other details
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

# --- Display Components with Ask AI Why Button ---
components = st.session_state.controller.get_components()
if components:
    st.header("Client Architecture Components")
    for comp in components:
        with st.expander(f"{comp.get('Name', 'Unnamed Component')}"):
            category = comp.get('Category', 'N/A')
            spend_val = comp.get('Spend', 0)
            st.write(f"**Category:** {category}")
            st.write(f"**Spend:** ${spend_val:,}")
            st.write(f"**Renewal Date:** {comp.get('Renewal Date', 'TBD')}")
            st.write(f"**Risk Score:** {comp.get('Risk Score', 5)}/10")

            if st.button(f"Ask AI Why ({comp['Name']})"):
                        reasoning = assist_modernization_reasoning(
                            comp.get('Name', 'Unknown'),
                            category,
                            spend_val,
                            renewal,
                            risk_score
                        )
                        st.success(reasoning)

        for i, comp in enumerate(components):  # Add an index for uniqueness
            with st.expander(f"{comp.get('Name', 'Unnamed Component')}"):
        # Ensure unique button label using UUID or memory address of the component
                unique_button_label = f"Ask AI Why ({comp.get('Name', 'Component')}) - {i} - {uuid.uuid4()}"
                if st.button(unique_button_label):
                    reasoning = assist_modernization_reasoning(
                comp.get('Name', 'Unknown'),
                comp.get('Category', 'N/A'),
                comp.get('Spend', 0),
                comp.get('Renewal Date', 'TBD'),
                comp.get('Risk Score', 5)
            )
                    st.success(reasoning)

# --- Simple Modernization Advisor Chatbot MVP ---
st.subheader("Modernization Chatbot")
user_input = st.chat_input("Ask about a component...")
if user_input:
    found = False
    for comp in components:
        if user_input.lower() in comp.get('Name', '').lower():
            reasoning = assist_modernization_reasoning(
                comp.get('Name', 'Unknown'),
                comp.get('Category', 'N/A'),
                comp.get('Spend', 0),
                comp.get('Renewal Date', 'TBD'),
                comp.get('Risk Score', 5)
            )
            st.success(reasoning)
            found = True
            break
    if not found:
        st.error("Component not found. Please try again.")

# Updated generate_roadmap_pdf with revenue + KPI injection

def generate_roadmap_pdf():
    import re
   
    # Optional fallback if bs4 isn't available
    try:
        from bs4 import BeautifulSoup
        bs4_available = True
    except ImportError:
        bs4_available = False

    pdf = FPDF()
    pdf.add_page()

    # --- Header and Meta ---
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

    # --- Revenue Section ---
    revenue_str = st.session_state.get("project_revenue", "$0")
    match = re.search(r"\$([\d,]+)", revenue_str)
    revenue_val = int(match.group(1).replace(",", "")) if match else 0
    components = st.session_state.controller.get_components()
    total_spend = sum(c.get("Spend", 0) for c in components)
    itrm_ratio = round((total_spend / revenue_val) * 100, 2) if revenue_val else 0

    pdf.ln(10)
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, "Financial Overview", ln=True)
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, f"Total Project Revenue: {revenue_str}", ln=True)
    pdf.cell(0, 10, f"Total IT Architecture Spend: ${total_spend:,.2f}", ln=True)
    pdf.cell(0, 10, f"ITRM KPI (Spend / Revenue): {itrm_ratio}%", ln=True)

    pdf.ln(10)
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, "Architecture Components:", ln=True)
    pdf.set_font("Helvetica", size=12)

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

# Generate PDF Button
if st.button("📄 Generate Modernization Roadmap PDF"):
    pdf_path = generate_roadmap_pdf()
    with open(pdf_path, "rb") as pdf_file:
        st.download_button(
            label="📥 Download Roadmap PDF",
            data=pdf_file,
            file_name=os.path.basename(pdf_path),
            mime="application/pdf"
        )

# --- Matplotlib Component Risk Plot Fix ---
components_df = pd.DataFrame(st.session_state.controller.get_components())
if not components_df.empty and "Name" in components_df and "Risk Score" in components_df:
    components_df_sorted = components_df.sort_values(by="Risk Score", ascending=True)
    components_df_sorted["Name"] = components_df_sorted["Name"].fillna("Unnamed").astype(str)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(
    components_df_sorted['Name'].astype(str),
    pd.to_numeric(components_df_sorted['Risk Score'], errors='coerce').fillna(0)
)
    ax.set_xlabel("Risk Score")
    ax.set_title("Component Risk Overview")
    st.pyplot(fig)




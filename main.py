import streamlit as st
import os
import json
import uuid
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
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
    "Storage": ["Pure Storage", "NetApp", "Dell EMC"],
    "Cybersecurity": ["CrowdStrike", "Palo Alto", "SentinelOne"],
    "BC/DR": ["Zerto", "Veeam", "AWS DRaaS"],
    "Compliance": ["OneTrust", "TrustArc", "Drata"]
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
    if category == "Cybersecurity" and risk_score > 7:
        suggestion += "Implement XDR and Zero-Trust Architecture to harden security posture. "
    if category == "BC/DR" and spend > 50000:
        suggestion += "Migrate to DRaaS platforms for more resilient disaster recovery. "
    if category == "Compliance" and risk_score > 6:
        suggestion += "Consider Compliance-as-a-Service (CaaS) offerings to streamline regulatory adherence. "
    if not suggestion:
        suggestion = "Review current asset lifecycle and evaluate modernization opportunities based on strategic goals."
    return suggestion

# --- Architecture Importer v2 (Visio, PDF, CSV, JSON) ---
st.header("📥 Upload Architecture Document")
uploaded_file = st.file_uploader("Upload Visio (.vsdx), PDF, CSV, or JSON", type=["vsdx", "pdf", "csv", "json"])

# Dynamic CSV Template Generator
template_df = pd.DataFrame({
    "Name": ["Example Component"],
    "Category": ["Hardware"],
    "Spend": [100000],
    "Renewal Date": ["2026-12-31"],
    "Risk Score": [5]
})

template_buffer = BytesIO()
template_df.to_csv(template_buffer, index=False)
template_buffer.seek(0)

st.download_button(
    label="📄 Download CSV Template",
    data=template_buffer,
    file_name="architecture_template.csv",
    mime="text/csv"
)

simulated_components = []
imported_batch = []

if uploaded_file:
    st.success(f"Uploaded: {uploaded_file.name}")
    file_extension = uploaded_file.name.split(".")[-1]

    if file_extension == "csv":
        df = pd.read_csv(uploaded_file)
        for _, row in df.iterrows():
            comp = {
                "Name": row.get("Name", "Unnamed Component"),
                "Category": row.get("Category", "Unknown"),
                "Spend": int(row.get("Spend", 0)),
                "Renewal Date": row.get("Renewal Date", "TBD"),
                "Risk Score": int(row.get("Risk Score", 5))
            }
            simulated_components.append(comp)
    else:
        simulated_components = [
            {"Name": "Core Router", "Category": "Networking", "Spend": 120000, "Renewal Date": "2025-12-31", "Risk Score": 7},
            {"Name": "Application Server", "Category": "Hardware", "Spend": 250000, "Renewal Date": "2026-06-30", "Risk Score": 5},
            {"Name": "Corporate Firewall", "Category": "Security", "Spend": 95000, "Renewal Date": "2025-04-15", "Risk Score": 8}
        ]

    if simulated_components:
        st.subheader("🔎 Parsed Components Preview")
        for comp in simulated_components:
            st.write(f"- {comp['Name']} ({comp['Category']}) | Spend: ${comp['Spend']:,} | Risk: {comp['Risk Score']}")

        if st.button("➕ Import Parsed Components into Architecture"):
            for comp in simulated_components:
                st.session_state.controller.add_component(comp)
                imported_batch.append(comp)
            st.success("Components successfully imported into current architecture!")

# Undo Last Import Option
if imported_batch:
    if st.button("↩️ Undo Last Import"):
        for comp in imported_batch:
            st.session_state.controller.remove_component_by_name(comp["Name"])
        imported_batch.clear()
        st.success("Last imported components removed!")
            
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

# --- Polished AIOps-Specific Risk Insights Dashboard ---
if st.session_state.controller.get_components():
    with st.expander("🚨 View AIOps Risk Insights Dashboard", expanded=True):
        components_df = pd.DataFrame(st.session_state.controller.get_components())

        expiring_soon = components_df[pd.to_datetime(components_df['Renewal Date'], errors='coerce') <= pd.to_datetime('2026-06-30')]
        high_risk = components_df[components_df['Risk Score'] >= 7]

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Components", len(components_df))
        col2.metric("Contracts Expiring by Mid-2026", len(expiring_soon))
        col3.metric("High Risk Components", len(high_risk))

        st.markdown("---")
        tab1, tab2, tab3 = st.tabs(["🛑 Expiring Contracts", "🔥 High Risk Components", "🛠️ Risk Delta Simulation"])

        with tab1:
            if not expiring_soon.empty:
                st.dataframe(expiring_soon[['Name', 'Category', 'Spend', 'Renewal Date', 'Risk Score']])
            else:
                st.info("✅ No contracts expiring soon.")

        with tab2:
            if not high_risk.empty:
                st.dataframe(high_risk[['Name', 'Category', 'Spend', 'Renewal Date', 'Risk Score']])
            else:
                st.info("✅ No high-risk components identified.")

        with tab3:
            st.subheader("🔧 Simulate Risk Score After Modernization")
            selected_component = st.selectbox("Select a component to simulate: ", components_df['Name'].unique())

            if selected_component:
                original_score = components_df.loc[components_df['Name'] == selected_component, 'Risk Score'].values[0]
                st.write(f"Original Risk Score: {original_score}")

                simulated_delta = st.slider("Simulated Risk Improvement (%)", min_value=0, max_value=100, value=20, step=5)
                simulated_new_score = max(0, original_score * (1 - simulated_delta/100))

                st.metric("Projected New Risk Score", round(simulated_new_score, 1))

                if st.button("💾 Save Simulated New Risk Score"):
                    for i, comp in enumerate(st.session_state.controller.get_components()):
                        if comp['Name'] == selected_component:
                            st.session_state.controller.components[i]['Risk Score'] = round(simulated_new_score, 1)
                            break
                    st.success(f"Updated {selected_component}'s risk score to {round(simulated_new_score, 1)}.")

            if st.button("♻️ Reset All Simulated Risk Scores"):
                # Assume we reset all components back to original baseline score of 8 for demo purposes
                for i, comp in enumerate(st.session_state.controller.get_components()):
                    if 'Original Risk Score' in comp:
                        st.session_state.controller.components[i]['Risk Score'] = comp['Original Risk Score']
                    else:
                        st.session_state.controller.components[i]['Risk Score'] = 8
                st.success("All risk scores reset to default values!")

        st.markdown("---")
        st.subheader("📈 Risk Score Comparison Across Components")
        fig, ax = plt.subplots(figsize=(10, 5))
        components_df_sorted = pd.DataFrame(st.session_state.controller.get_components()).sort_values(by="Risk Score", ascending=False)
        ax.barh(components_df_sorted['Name'], components_df_sorted['Risk Score'])
        ax.set_xlabel('Risk Score')
        ax.set_title('Component Risk Scores After Simulation')
        st.pyplot(fig)

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

            avg_market_spend = simulate_external_pricing_lookup(category)
            st.write(f"**Industry Average Spend:** ~${avg_market_spend:,}")
            if avg_market_spend:
                variance = ((spend_val - avg_market_spend) / avg_market_spend) * 100
                st.write(f"**Variance:** {variance:+.1f}% vs. Market")

            aws_cloud_cost = simulate_aws_cloud_pricing(category, spend_val)
            cloud_savings = spend_val - aws_cloud_cost
            st.write(f"**AWS Cloud Alternative:** ~${aws_cloud_cost:,}")
            st.write(f"**Potential Cloud Migration Savings:** ~${cloud_savings:,}")

            if category in ["Hardware", "Storage", "Cloud"]:
                service_pricing = simulate_aws_service_pricing("EC2" if category == "Hardware" else "S3")
                st.write(f"**Simulated AWS Service Pricing:** ~${service_pricing}/month")

            if st.button(f"Ask AI Why ({comp.get('Name', 'Component')})"):
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

# --- PDF Export with Executive Summary and Detailed Roadmap ---
def generate_roadmap_pdf():
    components = st.session_state.controller.get_components()
    total_spend, total_cloud_spend, category_counts, top_risks = generate_executive_summary(components)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "ITRM Modernization Executive Summary", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Total Current Spend: ${total_spend:,}", ln=True)
    pdf.cell(0, 10, f"Total Estimated Cloud Spend: ${total_cloud_spend:,}", ln=True)
    pdf.cell(0, 10, f"Potential Cloud Migration Savings: ${total_spend - total_cloud_spend:,}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Component Category Distribution:", ln=True)
    pdf.set_font("Arial", size=12)
    for cat, count in category_counts.items():
        pdf.cell(0, 8, f"- {cat}: {count} Components", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Top 5 High-Risk / High-Spend Components:", ln=True)
    pdf.set_font("Arial", size=12)
    for name, cat, spend, risk in top_risks:
        pdf.cell(0, 8, f"- {name} ({cat}) | Spend: ${spend:,} | Risk Score: {risk}", ln=True)

    # --- Add Detailed Roadmap Section ---
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "ITRM Modernization Detailed Roadmap", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    for comp in components:
        name = comp.get("Name", "Unnamed")
        category = comp.get("Category", "Other")
        spend_val = comp.get("Spend", 0)
        renewal = comp.get("Renewal Date", "TBD")
        risk_score = comp.get("Risk Score", 5)

        modernization = dynamic_generate_modernization_suggestion(category, spend_val, renewal, risk_score)
        savings = generate_spend_saving_estimate(category, spend_val, modernization)

        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 8, f"Component: {name}", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 8, f"Category: {category}", ln=True)
        pdf.cell(0, 8, f"Spend: ${spend_val:,}", ln=True)
        pdf.cell(0, 8, f"Renewal Date: {renewal}", ln=True)
        pdf.cell(0, 8, f"Risk Score: {risk_score}/10", ln=True)
        pdf.multi_cell(0, 8, f"Modernization Suggestion: {modernization}")
        pdf.cell(0, 8, savings, ln=True)
        pdf.ln(5)

    output_dir = "generated_pdfs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filename = f"{output_dir}/ITRM_Modernization_Roadmap.pdf"
    pdf.output(filename)

    return filename

# --- Streamlit Button to Generate Modernization PDF ---
if st.button("🚀 Generate Full Modernization Roadmap PDF"):
    pdf_path = generate_roadmap_pdf()
    if pdf_path:
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Download Modernization Roadmap PDF",
                data=f,
                file_name="Modernization_Roadmap.pdf",
                mime="application/pdf"
            )

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






import streamlit as st
import pandas as pd

# Embedded grouped questions JSON (shortened for readability — insert full content below)
grouped_questions = {
    "Managed / Automated": [
        "Failover between sites",
        "Software Intelligence",
        "Converged Infrastructure standardization",
        "Replication",
        "User Defined Recovery",
        "•Standard set of OS, MW, DB instances, customization by exception",
        "Non-Disruptive Upgrades",
        "Automated Capacity Upgrade",
        "Dynamic Resource Pools",
        "Workflow automation encapsulating  best practice availability management",
        "Capacity Automation Triggers",
        "Admin assisted provisioning of users privileges",
        "Federated access to multiple systems",
        "Customer and business focused, IT service and delivery centric organization, formal governance",
        "Formal IT management processes/tools/architecture; shared services; aggregated capacity management ",
        "IT service cost metrics",
        "Dynamic optimization of IT services; consolidated converged operations IT staff",
        "Extensive infrastructure monitoring for availability",
        "Automated failover of resources; always on",
        "Workload independence and prioritization",
        "Mulit-Tenancy security enabled",
        "•Allocations based on cost neutral / cost recovery method (cost center approach)"
    ],
    "Awareness, measured, semi-automated": [
        "Parameters Identified to evaluate each silo ",
        "Standardized silo hardware",
        "Standardized Back Up System",
        "•Limited OS / MW rationalization (multiple OS versions, multiple database versions)",
        "ITSM governance oversight of tools/scripts",
        "Centralized authentication (e.g. RADIUS, TACACS+, LDAP, 802.1x)",
        "Defined IT organization for infrastructure and operations",
        "Site to Site Replication",
        "•Cost allocation based on  technology components"
    ],
    "Private x As a Service (xAAS)": [
        "Single Call Support",
        "Software Intelligence",
        "Capacity management meets demand",
        "Network Roles, flows, and key sequences are continually monitored and measured for performance",
        "User restoration capabilities",
        "Shared Pools of Resources"
    ],
    "Awareness, measured, semi-automated                                 Consolidated": [
        "Multiple VMs/Server",
        "Application not tied to physical infrastructure",
        "Reporting Identified",
        "Capacity Planing Capable",
        "Multi site delivery"
    ],
    "Business Partnership/Innovation Optimized": [
        "Virtualized Pool of Resources",
        "User defined back up",
        "•Limited, standard OS images – forced compliance of use, no customization",
        "User provisioning of defined IT service catalog applications – self service portal",
        "Orchestration is initiated by user portal",
        "No E2E service impact from security exposure",
        "Dynamic optimization of IT services; consolidated converged operations IT staff",
        "Application resources pooled across multiple data centers",
        "•Accurate activity based costing (ABC) models"
    ],
    "Committed, Continuous Improvement, Redundant": [
        "Upgrade Schedule Formalized",
        "Point in Time Restoration",
        "•Standardized / rationalized OS to hypervisor supported instances",
        "Standard templates evolve from analyzing provisioning patterns",
        "Risks and impact to E2E service must be included for provision, assurance and dialogue services.",
        "Technology centric organization; investment in IT service desk function and staff",
        "Configuration/Policy/Capacity management at the SW layer, not HW layer",
        "•Cost allocation based on necessary bundled infrastructure components (i.e. servers, storage, network)"
    ],
    "Committed, Continuous Improvement, Redundant Virtualized": [
        "Upgrade Roadmap",
        "Failover capability",
        "Capacity on Demand",
        "Financial Metrics identified"
    ],
    "Consolidated ": [
        "Reference architecture standards",
        "Network sequences or value flows are repeatable",
        "SLA defined timelines and restoration",
        "RPO/RTO Defined",
        "Applications Categorized"
    ],
    "Service Aligned/Standardization/High Availability": [
        "No Single Point of Failure",
        "Data Deduplication",
        "•Gold instances of OS, MW, DB for automated provisioning",
        "Application classification",
        "Service Level Management "
    ],
    "Survival, Ad-Hoc, Manual Legacy ": [
        "Network consists of routers, switches, LAN/WAN",
        "Separate, multi-vendor individual servers providing single use/application services per server",
        "Separate, multi-vendor individual storage providing single use/application services per storage",
        "Back Up for restoring in case of data center disaster",
        "Non-uniform custom racks, power connections, and cable management."
    ],
    "Virtualized": [
        "Failover within Silo and Infrastructure",
        "Converged Infrastructure adoption",
        "Manufactured HW/CI out of the factory",
        "Network defined and documented standard sequences and specific transactions between roles",
        "Network metrics are used effectively to control different flows and sequence variations"
    ]
}
st.set_page_config(page_title="IT Maturity Assessment", layout="wide")
st.title("🧠 IT Maturity Assessment Tool")
st.markdown("""
Welcome to the interactive IT Maturity Assessment. Please answer the following questions 
based on your current IT environment. Your responses will be used to calculate a maturity score
across several technology domains.
""")

responses = {}
st.sidebar.header("Navigation")

# Questionnaire Form
with st.form("maturity_form"):
    for category, questions in grouped_questions.items():
        st.subheader(category.strip())
        for q in questions:
            key = f"{category.strip()}::{q}"
            responses[key] = st.radio(q.strip(), ["Yes", "No"], key=key)
    submitted = st.form_submit_button("Submit Assessment")

# Scoring and Results
if submitted:
    st.header("📊 Maturity Assessment Results")
    score_data = []

    for category in grouped_questions:
        questions = grouped_questions[category]
        yes_count = sum(
            1 for q in questions if responses.get(f"{category.strip()}::{q}") == "Yes"
        )
        total = len(questions)
        percent = round((yes_count / total) * 100, 1)
        score_data.append({"Category": category.strip(), "Score (%)": percent})

    score_df = pd.DataFrame(score_data).sort_values(by="Category")
    st.dataframe(score_df, use_container_width=True)

    # Heatmap visual (Streamlit-compatible, no matplotlib)
    st.subheader("🔵 Heatmap View of Maturity by Category")
    st.dataframe(score_df.style.format({"Score (%)": "{:.1f}"}))

    # Bar chart view
    st.subheader("📈 Bar Chart of Scores")
    st.bar_chart(score_df.set_index("Category"))

    
    st.markdown("""
### 🔍 Interpretation:
    - **80%+**: High maturity — optimized or automated
    - **50-79%**: Moderate maturity — standardized or in transition
    - **Below 50%**: Low maturity — ad-hoc or siloed
    """)

    # Recommendations Section
    st.header("🧭 Recommendations by Category")
    for _, row in score_df.iterrows():
        score = row["Score (%)"]
        category = row["Category"]
        if score >= 80:
            rec = f"✅ *{category}* is highly mature. Continue optimizing with automation and cross-domain integration."
        elif score >= 50:
            rec = f"⚠️ *{category}* shows moderate maturity. Focus on standardization, consolidation, and governance improvements."
        else:
            rec = f"❌ *{category}* is low maturity. Prioritize modernization, documentation, and automation."
        st.markdown(rec)

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.bootstrap import page_bootstrap
from utils.session_state import initialize_session
initialize_session()
from utils.ai_assist import generate_maturity_recommendation
from utils.auth import enforce_login
enforce_login()

# Embedded grouped questions JSON (shortened for readability — insert full content below)
grouped_questions = {
    "Survival / Legacy / Ad-Hoc": [
        "Infrastructure is manually provisioned with minimal automation.",
        "Separate physical servers and storage are used for each workload.",
        "Backups exist but are manual and inconsistently tested.",
        "No formal incident response process or security oversight.",
        "Monitoring is siloed or reactive only."
    ],
    "Standardized / Service-Aligned": [
        "Standard operating environments (SOEs) exist for OS, middleware, and database.",
        "IT service management (ITSM) processes are documented and partially adopted.",
        "SLAs and RTO/RPOs are defined for key applications.",
        "Service request and incident tracking is centralized (e.g. via ITSM tool).",
        "Network architecture is documented and maintained to reference standards."
    ],
    "Virtualized / Cloud-Ready": [
        "Most workloads are virtualized or containerized.",
        "Cloud usage (public/private) is governed via policy.",
        "Infrastructure is provisioned through templates or IaC (e.g., Terraform, CloudFormation).",
        "Role-based access controls are centrally managed.",
        "Security patches and updates are deployed on a defined schedule."
    ],
    "Automated / Observability-Driven": [
        "Infrastructure provisioning and app deployment are fully automated via CI/CD.",
        "Centralized observability is in place (e.g., logs, metrics, traces).",
        "Configuration drift is automatically detected and remediated.",
        "Automated testing is included in deployment pipelines.",
        "Automated scaling and self-healing systems are in use."
    ],
    "Business-Aligned / Self-Service": [
        "Business KPIs are directly tied to IT service metrics and dashboards.",
        "Users can self-provision services from a defined catalog.",
        "Cost allocation is activity-based or tagged per service/user/project.",
        "Cross-functional teams collaborate on IT planning and forecasting.",
        "IT investment decisions are driven by business value and outcome modeling."
    ],
    "Innovative / Predictive / Autonomous": [
        "AI/ML is used for predictive capacity planning or anomaly detection.",
        "Security is integrated into CI/CD pipelines (DevSecOps).",
        "Cloud cost optimization is automated with policy-based actions.",
        "Disaster recovery and failover are tested regularly and auto-validated.",
        "Digital twin or simulation models are used for infrastructure planning."
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

page_bootstrap(current_page="IT Assessment")  # Or "Risk Model", etc.

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
    
    st.session_state['it_maturity_scores'] = score_df
    
    # Heatmap visual (Streamlit-compatible, no matplotlib)
    st.subheader("🔵 Heatmap View of Maturity by Category")
    st.dataframe(
    score_df.style
        .format({"Score (%)": "{:.1f}"})
        .background_gradient(cmap="RdYlGn", subset=["Score (%)"])
)

    st.subheader("📈 Bar Chart of Scores (Color-Coded)")
    
    fig = px.bar(
        score_df,
        x="Category",
        y="Score (%)",
        color="Score (%)",
        color_continuous_scale="RdYlGn",
        range_y=[0, 100],
        text="Score (%)",
        title="IT Maturity by Category"
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    
    st.markdown("""
### 🔍 Interpretation:
    - **80%+**: High maturity — optimized or automated
    - **50-79%**: Moderate maturity — standardized or in transition
    - **Below 50%**: Low maturity — ad-hoc or siloed
    """)

# Recommendations Section
st.header("🧭 Recommendations by Category")

# Clear old recommendations once
st.session_state["it_maturity_recommendations"] = []

    for _, row in score_df.iterrows():
        score = row["Score (%)"]
        category = row["Category"]
    
        if score >= 80:
            rec = f"✅ *{category}* is highly mature. Continue optimizing with automation and cross-domain integration."
            rec_text = None
        elif score < 50:
            with st.spinner(f"🔍 Generating AI recommendation for {category}..."):
                rec_text = generate_maturity_recommendation(category)
            rec = f"❌ *{category}* is low maturity.\n\n🔧 **AI Recommendation:** {rec_text}"
        else:
            rec = f"⚠️ *{category}* shows moderate maturity. Focus on standardization, consolidation, and governance improvements."
            rec_text = None
    
        st.markdown(rec)
    
        st.session_state["it_maturity_recommendations"].append({
            "category": category,
            "score": score,
            "recommendation": rec_text
        })

# ---------------- Admin Tab: Edit Questions ----------------
st.markdown("---")
st.subheader("✏️ Edit Assessment Questions")

if 'grouped_questions' not in st.session_state:
    st.session_state.grouped_questions = grouped_questions.copy()

edited_category = st.selectbox("Select Category to Edit", list(st.session_state.grouped_questions.keys()))
new_question = st.text_input("Add a new question to this category:")

if st.button("➕ Add Question") and new_question:
    st.session_state.grouped_questions[edited_category].append(new_question)
    st.success(f"Question added to {edited_category}!")

if st.button("🗑️ Remove Last Question") and st.session_state.grouped_questions[edited_category]:
    removed = st.session_state.grouped_questions[edited_category].pop()
    st.warning(f"Removed: {removed}")

st.markdown("### Current Questions in Selected Category:")
st.write(st.session_state.grouped_questions[edited_category])

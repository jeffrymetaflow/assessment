# --- AI Maturity Assessment (Combined Input & Output) ---
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.bootstrap import page_bootstrap
from utils.session_state import initialize_session
from utils.auth import enforce_login
from controller.supabase_controller import save_session_to_supabase
from utils.ai_assist import generate_ai_maturity_recommendation_with_products

initialize_session()
enforce_login()

st.set_page_config(page_title="AI Maturity Assessment", layout="wide")
st.title("🤖 AI Maturity Assessment")

# --- Define AI Maturity Categories & Questions ---
grouped_questions = {
    "Infrastructure and Technology": [
        "Do you have a robust data storage solution that can handle large volumes of data?",
        "Is your network infrastructure capable of supporting high-speed data transfer?",
        "Do you have cloud services integrated into your technology stack?",
        "Are you utilizing modern programming languages and frameworks suitable for AI development?",
        "Do you have secure systems in place to protect sensitive data from cyber threats?",
        "Is there a dedicated platform for AI experimentation and deployment available within your organization?",
        "Are your hardware resources (like GPUs) sufficient for AI processing needs?",
        "Do you monitor and manage compute resource utilization for AI workloads?",
        "Are edge devices or IoT integrations part of your AI architecture?",
        "Do you have observability tools in place to monitor AI system performance and availability in real time?"
    ],
    "Data Management and Quality": [
        "Do you have a centralized data repository for easy access to data across departments?",
        "Is your data regularly cleaned and updated to ensure accuracy?",
        "Do you have established protocols for data governance and compliance?",
        "Is your organization collecting data relevant to your AI use cases?",
        "Are there processes in place to assess and improve data quality continuously?",
        "Is there an existing strategy for data privacy that aligns with legal standards?",
        "Do you have historical data available for training AI models?",
        "Is metadata consistently captured and maintained across datasets?",
        "Do you use data catalogs or data lineage tools?",
        "Are data access controls in place to ensure only authorized personnel can retrieve or manipulate critical datasets?"
    ],
    "Talent and Skills": [
        "Do you have employees with expertise in data science or machine learning?",
        "Is there a training program in place to upskill staff in AI and related technologies?",
        "Are interdisciplinary teams formed to collaborate on AI projects?",
        "Is there a clear understanding of AI concepts and terminology among your leadership team?",
        "Do you have access to external AI consultants or partnerships?",
        "Is there a culture of innovation that encourages risk-taking and experimentation?",
        "Are you actively recruiting for AI-related positions?",
        "Do you have product managers or business analysts involved in AI use case definition?",
        "Do project teams have access to MLOps or model deployment skills?",
        "Do you have a succession or continuity plan for key AI/ML personnel or roles?"
    ],
    "Strategy and Vision": [
        "Do you have a clear AI strategy that aligns with your business goals?",
        "Is there a dedicated budget allocated for AI projects?",
        "Are there measurable KPIs established to track the success of AI initiatives?",
        "Do you have a roadmap for AI implementation over the next 1–3 years?",
        "Are you regularly revisiting and updating your AI strategy based on industry trends?",
        "Is there commitment from executive leadership to support AI initiatives?",
        "Are AI projects prioritized based on their potential business impact?",
        "Is AI considered a core enabler in your digital transformation agenda?",
        "Do you conduct regular reviews of AI use cases to ensure alignment with ROI?",
        "Have business units been engaged in identifying and prioritizing AI use cases that address real operational pain points?"
    ],
    "Ethics and Governance": [
        "Do you have an ethical framework guiding your AI initiatives?",
        "Is there a process for assessing the potential biases in your AI models?",
        "Are you transparent with stakeholders about how AI is used in your organization?",
        "Do you have mechanisms in place to address public concerns about AI?",
        "Have you established guidelines for responsible AI use?",
        "Is there a designated team responsible for monitoring AI compliance and ethics?",
        "Are stakeholders involved in discussions about the ethical implications of AI applications?",
        "Is there a protocol for handling model failures or unintended AI behavior?",
        "Do you track AI model performance post-deployment for fairness and drift?",
        "Is there a clear audit trail or documentation process for how AI decisions are made in critical applications?"
    ]
}

# --- INPUT FORM ---
if st.sidebar.radio("Select Tab", ["📝 Input Assessment", "📊 View Results"], horizontal=True) == "📝 Input Assessment":
    st.subheader("📝 Complete the AI Maturity Assessment")

    if st.sidebar.button("🔄 Clear Assessment"):
        st.session_state.pop("ai_maturity_answers", None)
        st.experimental_rerun()

    if "ai_maturity_answers" not in st.session_state:
        st.session_state["ai_maturity_answers"] = {}

    with st.form("ai_maturity_form"):
        local_responses = {}

        for category, questions in grouped_questions.items():
            st.subheader(category)
            for q in questions:
                key = f"{category}::{q}"
                default = st.session_state["ai_maturity_answers"].get(key, "No")
                local_responses[key] = st.radio(
                    q, ["Yes", "No"], key=key, index=0 if default == "Yes" else 1
                )

        submitted = st.form_submit_button("Submit AI Assessment")

    if submitted:
        st.session_state["ai_maturity_answers"] = local_responses.copy()
        st.success("✅ Assessment Submitted & Saved.")
        save_session_to_supabase()

# --- OUTPUT TAB ---
else:
    if "ai_maturity_answers" not in st.session_state:
        st.warning("⚠️ No responses submitted yet. Please complete the assessment on the Input tab.")
        st.stop()

    score_data = {}
    for key, response in st.session_state["ai_maturity_answers"].items():
        category, _ = key.split("::", 1)
        if category not in score_data:
            score_data[category] = {"yes": 0, "total": 0}
        if response == "Yes":
            score_data[category]["yes"] += 1
        score_data[category]["total"] += 1

    score_rows = [
        {"Category": category, "Score (%)": round((data["yes"] / data["total"]) * 100, 1)}
        for category, data in score_data.items()
    ]

    score_df = pd.DataFrame(score_rows).sort_values(by="Category")
    st.session_state["ai_maturity_scores"] = score_df

    st.subheader("📈 Category Scores")
    st.dataframe(score_df, use_container_width=True)

    st.subheader("🔵 Heatmap View")
    st.dataframe(
        score_df.style
        .format({"Score (%)": "{:.1f}"})
        .background_gradient(cmap="RdYlGn", subset=["Score (%)"])
    )

    st.subheader("📊 Bar Chart")
    fig = px.bar(
        score_df,
        x="Category",
        y="Score (%)",
        color="Score (%)",
        color_continuous_scale="RdYlGn",
        range_y=[0, 100],
        text="Score (%)",
        title="AI Maturity by Category"
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    st.header("🧭 Recommendations by Category")
    st.session_state["ai_maturity_recommendations"] = []
    
    for _, row in score_df.iterrows():
        score = row["Score (%)"]
        category = row["Category"]
    
        rec_data = generate_ai_maturity_recommendation_with_products(category)
        rec_text = rec_data.get("recommendation", "")
        products = rec_data.get("products", [])
    
        st.session_state["ai_maturity_recommendations"].append({
            "category": category,
            "score": score,
            "recommendation": rec_text,
            "products": products
        })
    
        st.markdown(f"### {category} (Score: {score}%)")
        st.markdown(f"**Recommendation:** {rec_text}")
    
        if products and isinstance(products[0], dict):
            st.markdown("**Recommended Products/Services:**")
            df = pd.DataFrame(products)
            df = df.fillna("N/A")  # fallback for missing fields
            st.dataframe(df, use_container_width=True)
        else:
            st.markdown("**Recommended Products/Services:** _No specific products found_")

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.bootstrap import page_bootstrap
from utils.session_state import initialize_session
initialize_session()
from utils.ai_assist import generate_maturity_recommendation
from utils.auth import enforce_login
enforce_login()
from controller.supabase_controller import save_session_to_supabase

st.set_page_config(page_title="IT Maturity Assessment", layout="wide")

st.title("🧠 IT Maturity Assessment Tool")
st.markdown("""
Welcome to the interactive IT Maturity Assessment. Please answer the following questions 
based on your current IT environment. Your responses will be used to calculate a maturity score
across several technology domains.
""")

# ----------------- Clear Button -----------------
if st.sidebar.button("🔄 Clear Assessment"):
    if "it_maturity_answers" in st.session_state:
        del st.session_state["it_maturity_answers"]
        st.experimental_rerun()

# ----------------- Initialize or Load Answers -----------------
responses = st.session_state.get("it_maturity_answers", {})

# ----------------- Questionnaire Form -----------------
with st.form("maturity_form"):
    for category, questions in grouped_questions.items():
        st.subheader(category.strip())
        for q in questions:
            key = f"{category.strip()}::{q}"
            # Pre-fill with previous answer or default to "No"
            default = responses.get(key, "No")
            responses[key] = st.radio(q.strip(), ["Yes", "No"], key=key, index=0 if default == "Yes" else 1)
    submitted = st.form_submit_button("Submit Assessment")

# ----------------- Scoring and Results -----------------
if submitted:
    st.session_state["it_maturity_answers"] = responses.copy()
    st.header("📊 Maturity Assessment Results")
    score_data = []

    for category in grouped_questions:
        questions = grouped_questions[category]
        yes_count = sum(1 for q in questions if responses.get(f"{category.strip()}::{q}") == "Yes")
        total = len(questions)
        percent = round((yes_count / total) * 100, 1)
        score_data.append({"Category": category.strip(), "Score (%)": percent})

    score_df = pd.DataFrame(score_data).sort_values(by="Category")
    st.dataframe(score_df, use_container_width=True)

    st.session_state['it_maturity_scores'] = score_df

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

    # ---------------- Recommendations ----------------
    st.header("🧭 Recommendations by Category")
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

# ---------------- Save to Supabase ----------------
if st.button("💾 Save Project to Supabase"):
    save_session_to_supabase()

# ---------------- Last Saved Timestamp ----------------
if "project_data" in st.session_state:
    last_saved = st.session_state["project_data"].get("last_saved")
    if last_saved:
        st.caption(f"🕒 Last saved: {last_saved}")

import streamlit as st
import pandas as pd

# Load Questionnaire and Admin sheet
@st.cache_data
def load_questionnaire():
    df_q = pd.read_excel("Cybersecurity questionnaire.xlsx", sheet_name="Questionnaire")
    df_admin = pd.read_excel("Cybersecurity questionnaire.xlsx", sheet_name="Admin sheet")
    return df_q, df_admin

questionnaire_df, admin_df = load_questionnaire()

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Cybersecurity Maturity Assessment", layout="wide")
st.title("🛡️ Cybersecurity Maturity Assessment Tool")
tabs = st.tabs(["Assessment", "Admin Panel"])

# --- Tab 1: Assessment ---
with tabs[0]:
    st.markdown("""
    Welcome to the Cybersecurity Assessment. Please answer the following questions based on your current IT practices.
    """)

    grouped = questionnaire_df.groupby("Category")
    responses = {}

    for category, group in grouped:
        with st.expander(f"**{category}**"):
            for _, row in group.iterrows():
                q_id = f"q_{row['ID']}"
                response = st.radio(row["Question"], ["Yes", "No"], key=q_id)
                responses[q_id] = response

    if st.button("Submit Responses"):
        st.success("✅ Responses saved (mock - no backend yet).")
        st.json(responses)

# --- Tab 2: Admin Panel ---
with tabs[1]:
    st.subheader("🛠️ Admin Question Configuration")
    st.write("Below is the current question configuration loaded from the Admin sheet:")
    st.dataframe(admin_df, use_container_width=True)

    if st.checkbox("Enable editing mode"):
        edited_df = st.data_editor(admin_df, num_rows="dynamic")
        if st.button("Save Changes (mock)"):
            st.success("✅ Changes saved (mock - no backend yet).")
            st.dataframe(edited_df)


import streamlit as st
from controller.supabase_controller import save_project, get_projects_by_email

st.title("🔎 Supabase Project Read Test")

email = "jeff@example.com"

if st.button("Fetch Projects by Email"):
    projects = get_projects_by_email(email)
    if projects:
        st.success(f"✅ Found {len(projects)} project(s) for {email}")
        for proj in projects:
            st.json(proj)
    else:
        st.warning("⚠️ No projects found or error occurred.")

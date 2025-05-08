# controller/supabase_controller.py

from utils.supabase_client import supabase
from postgrest.exceptions import APIError

def save_project(project_data):
    """Insert a new project into Supabase"""
    try:
        response = supabase.table("projects").insert(project_data).execute()
        return response.data[0]
    except APIError as e:
        print("Save failed:", e)
        return None

def get_projects_by_email(email):
    """Fetch all projects associated with a given user email"""
    try:
        response = supabase.table("projects").select("*").eq("user_email", email).execute()
        return response.data
    except APIError as e:
        print("Fetch failed:", e)
        return []

def update_project_by_id(project_id, updated_data):
    """Update a project by its UUID"""
    try:
        response = supabase.table("projects").update(updated_data).eq("id", project_id).execute()
        return response.data[0] if response.data else None
    except APIError as e:
        print("Update failed:", e)
        return None

def save_session_to_supabase():
    """Save current session_state project data to Supabase"""
    if "project_data" not in st.session_state:
        st.warning("⚠️ No project loaded — nothing to save.")
        return None

    project_id = st.session_state["project_data"]["id"]

    # Build update payload — customize as needed
    updated_data = {
        "revenue": st.session_state.get("revenue"),
        "expenses": st.session_state.get("expenses"),
        "architecture": st.session_state.get("architecture"),
        "maturity_score": st.session_state.get("maturity_score"),
    }

    try:
        result = supabase.table("projects").update(updated_data).eq("id", project_id).execute()
        st.success("✅ Project saved to Supabase.")
        return result.data[0] if result.data else None
    except APIError as e:
        st.error("❌ Failed to save project to Supabase.")
        st.write(e)
        return None


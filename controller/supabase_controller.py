# controller/supabase_controller.py
import streamlit as st
from utils.supabase_client import supabase
from postgrest.exceptions import APIError
from datetime import datetime

def save_project(project_data):
    try:
        response = supabase.table("projects").insert(project_data).execute()
        print("Raw Supabase Response:", response)
        if response.data:
            return response.data[0]
        else:
            print("Save failed, data is None or empty")
            return None
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
    if "project_data" not in st.session_state:
        st.warning("⚠️ No project loaded — nothing to save.")
        return None

    if "id" not in st.session_state["project_data"]:
        st.error("❌ Project ID missing from project data. Please recreate or reload your project session.")
        return None

    project_id = st.session_state["project_data"]["id"]

    # ✅ Clean and safe: Only update session_data JSON column
    updated_data = {
        "session_data": {
            "maturity_score": st.session_state.get("maturity_score"),
            "maturity_answers": st.session_state.get("it_maturity_answers"),
            "cyber_answers": st.session_state.get("cybersecurity_answers"),
            "last_saved": datetime.utcnow().isoformat()
        },
        "user_email": st.session_state.get("user_email")
    }

    try:
        result = supabase.table("projects").update(updated_data).eq("id", project_id).execute()

        if result.data:
            st.session_state["project_data"] = result.data[0]
            st.success(f"✅ Project saved at {result.data[0]['updated_at']}")
        return result.data[0] if result.data else None
    except APIError as e:
        st.error("❌ Failed to save project to Supabase.")
        st.write(e)
        return None

def delete_project_by_id(project_id):
    """Deletes a project from Supabase by UUID"""
    try:
        result = supabase.table("projects").delete().eq("id", project_id).execute()
        return result
    except APIError as e:
        st.error("❌ Failed to delete project.")
        st.write(e)
        return None


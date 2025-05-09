# controller/supabase_controller.py
import streamlit as st
from utils.supabase_client import supabase
from postgrest.exceptions import APIError
from datetime import datetime

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
    if "project_data" not in st.session_state:
        st.warning("⚠️ No project loaded — nothing to save.")
        return None

    project_id = st.session_state["project_data"]["id"]

    updated_data = {
        "user_email": (
            st.session_state["project_data"].get("user_email")
            or st.session_state.get("user_email")
        ),
        "revenue": st.session_state.get("revenue"),
        "expenses": st.session_state.get("expenses"),
        "architecture": st.session_state.get("architecture"),
        "maturity_score": st.session_state.get("maturity_score"),
        "last_saved": datetime.utcnow().isoformat()
        "maturity_answers": st.session_state.get("it_maturity_answers")
    }


    try:
        result = supabase.table("projects").update(updated_data).eq("id", project_id).execute()

        # Update local session copy
        if result.data:
            st.session_state["project_data"] = result.data[0]
            st.success(f"✅ Project saved at {result.data[0]['last_saved']}")
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

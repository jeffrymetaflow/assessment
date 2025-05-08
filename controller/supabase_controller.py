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

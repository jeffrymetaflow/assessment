from utils.supabase_client import supabase

# Example usage:
result = supabase.table("projects").select("*").execute()

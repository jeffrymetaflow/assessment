import streamlit as st
from utils.supabase_client import supabase
from postgrest.exceptions import APIError

st.title("🔗 Supabase Test Insert")

data = {
    "user_email": "jeff@example.com",
    "project_name": "Pilot - Walmart",
    "revenue": 1500000,
    "maturity_score": 0.75
}

try:
    insert_result = supabase.table("projects").insert(data).execute()
    st.success("✅ Insert successful")
    st.json(insert_result.data)
except APIError as e:
    st.error("❌ Supabase API error occurred")
    st.write(e)

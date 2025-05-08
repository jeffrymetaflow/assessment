import streamlit as st
from utils.supabase_client import supabase
from supabase.lib.postgrest import APIError

st.title("🔗 Supabase Test Insert")

data = {
    "user_email": "jeff@example.com",
    "project_name": "Pilot - Walmart",
    "revenue": 1500000,
    "expenses": {"hardware": 400000, "software": 250000},
    "architecture": {"ERP": ["SAP", "Dell"], "Cloud": ["AWS"]},
    "maturity_score": 0.75
}

try:
    insert_result = supabase.table("projects").insert(data).execute()
    st.success("✅ Insert successful")
    st.json(insert_result.data)
except APIError as e:
    st.error("❌ Insert failed")
    st.json(e.args[0])

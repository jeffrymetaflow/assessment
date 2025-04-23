import streamlit as st
from utils.ai_assist import ai_assist_overlay

def page_bootstrap():
    with st.sidebar.expander("💬 AI Assistant", expanded=False):
        ai_assist_overlay()

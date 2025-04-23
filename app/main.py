import streamlit as st
from controller.controller import ITRMController

if "controller" not in st.session_state:
    st.session_state.controller = ITRMController()

st.title("💡 ITRM Platform")
st.write("Welcome! Use the tabs at the left to explore your IT strategy.")

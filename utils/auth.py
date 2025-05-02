import streamlit as st

def login():
    st.title("🔐 ITRM Access Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if (
            username == st.secrets["auth"]["username"] and
            password == st.secrets["auth"]["password"]
        ):
            st.session_state["authenticated"] = True
        else:
            st.error("❌ Incorrect credentials")

def enforce_login():
    if "authenticated" not in st.session_state:
        login()
        st.stop()

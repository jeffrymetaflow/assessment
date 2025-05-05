import streamlit as st
import requests
from openai import OpenAI
from utils.bootstrap import page_bootstrap
from utils.session_state import initialize_session
initialize_session()
from utils.auth import enforce_login
enforce_login()


st.set_page_config(page_title="🔌 API Key Test: OpenAI & Tavily", layout="wide")
st.title("🔌 Test Your API Keys: OpenAI & Tavily")

# Load secrets
openai_key = st.secrets.get("openai_api_key")
tavily_key = st.secrets.get("tavily_api_key")

# --- Test OpenAI ---
st.subheader("🤖 OpenAI Test")
if openai_key:
    try:
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello from OpenAI."}]
        )
        message = response.choices[0].message.content
        st.success("OpenAI connected successfully!")
        st.info(f"Response: {message}")
    except Exception as e:
        st.error(f"OpenAI connection failed: {e}")
else:
    st.warning("No OpenAI API key found in secrets.")

# --- Test Tavily ---
st.subheader("🔍 Tavily Test")
if tavily_key:
    try:
        headers = {"Authorization": f"Bearer {tavily_key}"}
        r = requests.post("https://api.tavily.com/search", json={"query": "What is Tavily?"}, headers=headers)
        if r.status_code == 200:
            st.success("Tavily connected successfully!")
            results = r.json().get("results", [])
            if results:
                st.write("Top Result:", results[0].get("title"))
            else:
                st.info("No search results returned.")
        else:
            st.error(f"Tavily API error: {r.status_code} - {r.text}")
    except Exception as e:
        st.error(f"Tavily connection failed: {e}")
else:
    st.warning("No Tavily API key found in secrets.")

from openai import OpenAI
client = OpenAI(api_key="your-key")
client.embeddings.create(input=["hello world"], model="text-embedding-ada-002")

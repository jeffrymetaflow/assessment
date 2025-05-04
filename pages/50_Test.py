import streamlit as st
import openai
import requests

st.set_page_config(page_title="🔌 API Key Test: OpenAI & Tavily", layout="wide")
st.title("🔌 Test Your API Keys: OpenAI & Tavily")

# Load secrets
openai.api_key = st.secrets.get("openai_api_key")
tavily_key = st.secrets.get("tavily_api_key")

# --- Test OpenAI ---
st.subheader("🤖 OpenAI Test")
if openai.api_key:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello from OpenAI."}]
        )
        message = response["choices"][0]["message"]["content"]
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

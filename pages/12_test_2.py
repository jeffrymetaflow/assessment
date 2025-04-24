import streamlit as st
import openai
import os
import json
from utils.intent_classifier import classify_intent
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search.tool import TavilySearchResults
import matplotlib.pyplot as plt
from PIL import Image
import pytesseract

st.set_page_config(page_title="IT Architecture - Financial Impact Mapper", layout="wide")
st.title("🧠 IT Architecture - Financial Impact Mapper")

st.markdown("### 🧩 Import from External Sources")
visio_file = st.file_uploader("Upload Visio Diagram (.vsdx)", type="vsdx")

if visio_file:
    st.success("✅ Visio diagram uploaded successfully. (Mock parser to be applied here)")
    st.write("Filename:", visio_file.name)

st.markdown("### 🌐 AI Ops API Connection")
aiops_token = st.text_input("Enter AI Ops API Token", type="password")
dynatrace_url = st.text_input("Dynatrace Base URL", placeholder="https://{your-env}.live.dynatrace.com")

if st.button("Fetch Architecture from Dynatrace"):
    if aiops_token and dynatrace_url:
        st.success("✅ Mock architecture fetched from Dynatrace")
        st.json({
            "infrastructure": [
                {"type": "VM", "name": "web-frontend-01", "status": "healthy"},
                {"type": "DB", "name": "orders-db", "status": "degraded"},
                {"type": "Cache", "name": "redis-main", "status": "healthy"}
            ],
            "alerts": [
                {"name": "High CPU on orders-db", "severity": "critical"},
                {"name": "Memory usage on redis-main", "severity": "warning"}
            ]
        })
    else:
        st.error("❌ Please provide both an API token and Dynatrace URL")

st.markdown("### 🏗️ Or Choose a Mock Architecture")
mock_architecture = st.selectbox("Select a predefined environment", ["Retail Storefront", "Healthcare System", "Banking Microservices"])

if mock_architecture:
    if mock_architecture == "Retail Storefront":
        st.json({
            "infra": ["Load Balancer", "Web Server", "POS Gateway", "SQL DB"],
            "alerts": ["POS latency spike", "Checkout API error rate"]
        })
    elif mock_architecture == "Healthcare System":
        st.json({
            "infra": ["Patient Portal", "FHIR API", "EHR Backend", "Imaging Server"],
            "alerts": ["EHR delay", "API auth failures"]
        })
    elif mock_architecture == "Banking Microservices":
        st.json({
            "infra": ["Auth Service", "Transaction Engine", "Ledger Store", "Notification Hub"],
            "alerts": ["Transaction timeout", "Ledger sync lag"]
        })

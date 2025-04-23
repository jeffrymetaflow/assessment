import streamlit as st
import openai
import os
from utils.intent_classifier import classify_intent
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search.tool import TavilySearchResults
import matplotlib.pyplot as plt
from PIL import Image
import pytesseract

# --- Architecture Upload and Interpretation ---
def architecture_component():
    st.title("🏗️ Architecture Ingestion & AIOps Preview")

    file = st.file_uploader("Upload Architecture Diagram (PDF, JPEG, or Visio)", type=["pdf", "jpeg", "jpg", "vsdx"])

    if file:
        file_type = file.type

        if file_type in ["image/jpeg", "image/jpg"]:
            image = Image.open(file)
            st.image(image, caption="Uploaded JPEG Architecture Diagram", use_column_width=True)

            st.markdown("### 🧠 Extracted Labels via OCR")
            extracted_text = pytesseract.image_to_string(image)
            st.text_area("Detected Text", value=extracted_text, height=200)

            if st.button("🤖 Analyze Diagram Text"):
                try:
                    openai_key = st.secrets["openai_api_key"]
                    os.environ["OPENAI_API_KEY"] = openai_key

                    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=openai_key)
                    agent = initialize_agent(
                        tools=[TavilySearchResults()],
                        llm=llm,
                        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                        verbose=False,
                        handle_parsing_errors=True
                    )

                    analysis_prompt = (
                        "Review this extracted architecture content and provide insight into potential risks, redundancies, \
                        and optimization opportunities in an enterprise IT environment:\n" + extracted_text
                    )

                    analysis_response = agent.run(analysis_prompt)
                    st.success(analysis_response)

                except Exception as e:
                    st.error(f"AI Analysis Error: {e}")

        elif file_type == "application/pdf":
            st.warning("🔧 PDF support coming soon for layered extraction and annotation.")

        elif file_type == "application/vnd.visio" or file.name.endswith(".vsdx"):
            st.warning("🔧 Visio parsing placeholder — convert to image or wait for AIOps API integration.")

        else:
            st.error("Unsupported file type.")

    else:
        st.info("📂 Upload an architecture file to begin analysis.")

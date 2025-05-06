import os
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from utils.vector_utils import load_vector_index  # adjust if needed
import streamlit as st

# Load OpenAI key securely from Streamlit secrets
openai_key = st.secrets.get("openai_api_key")

def answer_with_code_context(query: str):
    if not openai_key:
        return "❌ OpenAI API key not configured. Please check your Streamlit secrets."

    try:
        vectorstore = load_vector_index()
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        qa = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(temperature=0, api_key=openai_key),
            chain_type="stuff",
            retriever=retriever
        )
        return qa.run(query)
    except Exception as e:
        return f"❌ Error during AI execution: {e}"

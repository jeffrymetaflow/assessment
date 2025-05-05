import os
import streamlit as st
import pandas as pd
from typing import List
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.chains import RetrievalQA

# --- Load API Key Safely ---
openai_key = st.secrets.get("openai_api_key") or st.secrets.get("openai", {}).get("api_key")
if not openai_key:
    raise KeyError("OpenAI API key is missing. Please configure it in the Streamlit secrets.")

# --- Embed and Store ---
embedding_model = OpenAIEmbeddings(openai_api_key=openai_key)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)

VECTOR_INDEX_PATH = "vector_store/faiss_index"

# --- Initialize vector store (in-memory or persisted) ---
def build_vector_index(docs: List[str], save_path: str = VECTOR_INDEX_PATH):
    chunks = text_splitter.create_documents(docs)
    vectorstore = FAISS.from_documents(chunks, embedding_model)
    vectorstore.save_local(save_path)
    return vectorstore

# --- Load vector index ---
def load_vector_index(path: str = VECTOR_INDEX_PATH):
    return FAISS.load_local(path, embeddings=embedding_model, allow_dangerous_deserialization=True)

# --- Ask AI with context from indexed code/doc chunks ---
def answer_with_code_context(query: str):
    if not os.path.exists(VECTOR_INDEX_PATH):
        return "Vector index not found. Please build it first from your code or documentation."
    
    vectorstore = load_vector_index()
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    qa = RetrievalQA.from_chain_type(llm=ChatOpenAI(temperature=0, api_key=openai_key), chain_type="stuff", retriever=retriever)
    return qa.run(query)

# --- Utility to preview what was indexed ---
def preview_indexed_docs(path: str = VECTOR_INDEX_PATH):
    if not os.path.exists(path):
        return []
    vectorstore = load_vector_index()
    return vectorstore.docstore._dict.values()


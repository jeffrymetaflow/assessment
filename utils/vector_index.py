import streamlit as st
# Step 1: Load module content and metadata
import os
import glob
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Adjust as needed to match your repo structure
code_paths = glob.glob("src/**/*.py", recursive=True)
all_docs = []
for path in code_paths:
    loader = TextLoader(path, encoding='utf-8')
    all_docs.extend(loader.load())

# Step 2: Split text into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
split_docs = splitter.split_documents(all_docs)

# Step 3: Create vector store
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

embedding_model = OpenAIEmbeddings(openai_api_key=st.secrets["openai_api_key"])
vectorstore = FAISS.from_documents(split_docs, embedding_model)

# Step 4: Save to disk for reuse (optional)
vectorstore.save_local("vector_index")

# Step 5: Build retriever
doc_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# Step 6: Add retrieval to Smart Consultant agent (in ai_assist.py)
from langchain.chains import RetrievalQA
retrieval_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=doc_retriever,
    return_source_documents=True
)

def answer_with_code_context(prompt):
    result = retrieval_chain(prompt)
    return result['result']

import streamlit as st
import os
from utils.vector_index import build_vector_index, preview_indexed_docs
from utils.auth import enforce_login
enforce_login()

st.set_page_config(page_title="Vector Index Admin", layout="wide")
st.title("🧠 Vector Index Admin Console")

# --- 1. Show currently indexed documents ---
st.subheader("✅ Currently Indexed Modules")
docs = list(preview_indexed_docs())
if docs:
    for doc in docs:
        st.markdown(f"- {doc.metadata.get('source', 'Unnamed File')}")
else:
    st.info("No modules have been indexed yet.")

# --- 2. Upload new module for indexing ---
st.subheader("📂 Upload New Code or Documentation")
uploaded_files = st.file_uploader("Upload Python or Markdown files", type=["py", "md", "txt"], accept_multiple_files=True)

if uploaded_files:
    contents = []
    for f in uploaded_files:
        text = f.read().decode("utf-8")
        contents.append(text)
        st.success(f"✅ Loaded: {f.name}")
    
    if st.button("🔄 Build / Refresh Vector Index"):
        build_vector_index(contents)
        st.success("Vector index updated successfully!")

# --- 3. Summary Chart ---
st.subheader("📊 Module Indexing Summary")
indexed_count = len(docs)
target_modules = ["main.py", "component_mapping.py", "architecture.py", "ai_assist.py", "risk_simulator.py", "calculators.py"]
missing = [m for m in target_modules if not any(m in doc.metadata.get('source', '') for doc in docs)]

st.markdown("**Indexed Modules:**")
st.success(", ".join([m for m in target_modules if m not in missing]) or "None yet")

st.markdown("**Missing Modules:**")
st.warning(", ".join(missing) or "All modules indexed ✅")

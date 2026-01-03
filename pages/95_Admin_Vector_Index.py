import streamlit as st
import os
from utils.vector_index import build_vector_index, preview_indexed_docs
from utils.auth import enforce_login

# --- Authenticate
enforce_login()

# --- Page Configuration
st.set_page_config(page_title="Vector Index Admin", layout="wide")
st.title("🧠 Vector Index Admin Console")

# --- Section 1: View Indexed Modules
st.subheader("✅ Currently Indexed Modules")

docs = list(preview_indexed_docs())
if docs:
    for doc in docs:
        st.markdown(f"- `{doc.metadata.get('source', 'Unnamed File')}`")
else:
    st.info("No modules have been indexed yet.")

# --- Section 2: Upload New Files for Indexing
st.subheader("📂 Upload New Code or Documentation")

uploaded_files = st.file_uploader(
    "Upload Python, Markdown, or Text files",
    type=["py", "md", "txt"],
    accept_multiple_files=True
)

uploaded_contents = []
if uploaded_files:
    for file in uploaded_files:
        try:
            content = file.read().decode("utf-8")
            uploaded_contents.append(content)
            st.success(f"✅ Loaded: {file.name}")
        except Exception as e:
            st.warning(f"Failed to read {file.name}: {e}")

    if st.button("🔄 Build / Refresh Vector Index"):
        build_vector_index(uploaded_contents)
        st.success("✅ Vector index updated successfully!")

# --- Section 3: Module Indexing Summary
st.subheader("📊 Module Indexing Summary")

target_modules = [
    "main.py", "component_mapping.py", "architecture.py",
    "ai_assist.py", "risk_simulator.py", "calculators.py"
]

indexed_sources = [doc.metadata.get("source", "") for doc in docs]
missing_modules = [m for m in target_modules if not any(m in src for src in indexed_sources)]

st.markdown("**Indexed Modules:**")
st.success(", ".join(set(target_modules) - set(missing_modules)) or "None yet")

st.markdown("**Missing Modules:**")
st.warning(", ".join(missing_modules) or "All modules indexed ✅")

# --- Section 4: Auto-discover Source Files from Project
def auto_discover_files():
    discovered = []
    for root, _, files in os.walk("."):
        if any(excl in root for excl in [".venv", "__pycache__", "vector_store", ".git"]):
            continue
        for file in files:
            if file.endswith((".py", ".md", ".txt")):
                discovered.append(os.path.join(root, file))
    return discovered

st.subheader("🔍 Discover Local Source Files")

if st.checkbox("Auto-load source files from project"):
    discovered_files = auto_discover_files()
    st.write(f"Found {len(discovered_files)} source files:")
    st.code("\n".join(discovered_files[:10]) + ("\n..." if len(discovered_files) > 10 else ""))

# --- Section 5: Build Index from Discovered + Uploaded Files
if st.button("⚙️ Build Vector Index from Source and Uploads"):
    combined_texts = []

    if "discovered_files" in locals():
        for path in discovered_files:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    combined_texts.append(f.read())
            except Exception as e:
                st.warning(f"Skipped {path}: {e}")

    if uploaded_files:
        for file in uploaded_files:
            try:
                content = file.read().decode("utf-8")
                combined_texts.append(content)
            except Exception as e:
                st.warning(f"Upload error: {file.name} - {e}")

    if combined_texts:
        build_vector_index(combined_texts)
        st.success("✅ Vector index built successfully!")
    else:
        st.warning("⚠️ No valid files found or uploaded.")

# --- Section 6: Preview Indexed Chunks
st.subheader("📚 Preview Indexed Chunks")

for i, doc in enumerate(docs):
    with st.expander(f"Chunk {i+1} - {doc.metadata.get('source', 'Unknown')}"):
        st.code(doc.page_content[:1000])

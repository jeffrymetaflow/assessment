import streamlit as st
import os
from utils.vector_index import build_vector_index, preview_indexed_docs

st.set_page_config(page_title="Vector Index Admin", layout="wide")
st.title("🧠 Admin: Vector Index Builder")

st.markdown("Upload files or auto-load from project folders to build the AI assistant’s vector index.")

# --- Upload option ---
uploaded_files = st.file_uploader("Upload additional code/docs (.py, .md, .txt)", type=["py", "md", "txt"], accept_multiple_files=True)

# --- Auto-load .py/.md/.txt files from folders ---
def auto_discover_files():
    file_paths = []
    for root, _, files in os.walk("."):
        if any(excluded in root for excluded in [".venv", "__pycache__", "vector_store", ".git"]):
            continue
        for file in files:
            if file.endswith((".py", ".md", ".txt")):
                file_paths.append(os.path.join(root, file))
    return file_paths

if st.checkbox("🔍 Auto-load source files from project"):
    discovered = auto_discover_files()
    st.write(f"Found {len(discovered)} files:")
    st.code("\n".join(discovered[:10]) + ("\n..." if len(discovered) > 10 else ""))

# --- Trigger build ---
if st.button("⚙️ Build Vector Index from Source and Uploads"):
    texts = []
    if "discovered" in locals():
        for path in discovered:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    texts.append(f.read())
            except Exception as e:
                st.warning(f"Skipped {path}: {e}")
    if uploaded_files:
        for f in uploaded_files:
            try:
                texts.append(f.read().decode("utf-8"))
            except Exception as e:
                st.warning(f"Upload error: {f.name} - {e}")
    if texts:
        build_vector_index(texts)
        st.success("✅ Vector index built successfully!")
    else:
        st.warning("No valid files found or uploaded.")

# --- Preview ---
st.markdown("### 📚 Preview Indexed Chunks")
for i, doc in enumerate(preview_indexed_docs()):
    with st.expander(f"Chunk {i+1}"):
        st.code(doc.page_content[:1000])

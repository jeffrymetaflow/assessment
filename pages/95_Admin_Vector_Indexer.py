import streamlit as st
from utils.vector_index import build_vector_index, preview_indexed_docs

st.set_page_config(page_title="Vector Index Admin", layout="wide")
st.title("🛠️ Admin: Vector Index Builder")

st.markdown("Upload your app source code or documentation to build the AI assistant’s knowledge base.")

uploaded_files = st.file_uploader("Upload code/docs (.py, .md, .txt)", type=["py", "md", "txt"], accept_multiple_files=True)

if uploaded_files and st.button("Build Vector Index"):
    all_text = []
    for f in uploaded_files:
        text = f.read().decode("utf-8")
        all_text.append(text)
    build_vector_index(all_text)
    st.success("✅ Vector index built successfully!")

st.markdown("---")
st.markdown("### 📚 Preview Indexed Documents")

docs = preview_indexed_docs()
if docs:
    for i, d in enumerate(docs):
        with st.expander(f"Indexed Chunk {i+1}"):
            st.code(d.page_content[:1000])
else:
    st.info("No index found. Upload files and build the index first.")

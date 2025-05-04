import streamlit as st
import base64

st.set_page_config(page_title="📘 ITRM Help Guide", layout="wide")
st.title("📘 ITRM Platform Instruction Manual")

st.markdown("""
Use this page to read or download the official instruction manual for the ITRM platform. This guide walks through each module in the application and explains how to use the tool to its fullest potential.
""")

# Inline PDF Viewer
pdf_path = "assets/ITRM Instruction Manual.pdf"

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="850px" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

show_pdf(pdf_path)

# Download button
with open(pdf_path, "rb") as pdf_file:
    st.download_button(
        label="📥 Download ITRM Instruction Manual (PDF)",
        data=pdf_file,
        file_name="ITRM_Instruction_Manual.pdf",
        mime="application/pdf"
    )

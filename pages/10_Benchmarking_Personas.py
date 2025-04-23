import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import uuid
import numpy as np
from utils.bootstrap import page_bootstrap

st.set_page_config(page_title="Benchmarking_Personas", layout="wide")
st.title("📈 Benchmarking Personas")

page_bootstrap(current_page="Benchmarking Personas")  # Or "Risk Model", etc.

section = "📊 Benchmarking Personas"  # Define the variable

# Benchmarking & Persona Tab
if section == "📊 Benchmarking Personas":
    st.title("📊 Benchmarking Personas")

    industry = st.selectbox("Select Industry", ["Healthcare", "Financial Services", "Retail", "Manufacturing", "Education", "Other"])
    company_size = st.selectbox("Select Company Size", ["< 500 employees", "500–5000", "> 5000"])
    user_role = st.radio("Your Role", ["CIO", "IT Director", "IT Ops", "Finance", "Other"])

    st.session_state.client_profile = {
        "industry": industry,
        "company_size": company_size,
        "user_role": user_role
    }

    st.subheader("📈 Industry Benchmarks")
    benchmark_data = {
        "Healthcare": [80, 65, 60, 50, 35],
        "Financial Services": [85, 75, 70, 55, 40],
        "Retail": [70, 60, 55, 45, 30],
        "Manufacturing": [75, 68, 62, 50, 38],
        "Education": [65, 55, 50, 40, 25],
        "Other": [72, 60, 57, 46, 32]
    }
    benchmark_df = pd.DataFrame({
        "Category": ["Managed / Automated", "Standardized / Optimized", "Defined / Measured", "Reactive / Operational", "Survival, Ad-Hoc, Manual Legacy"],
        "Industry Average (%)": benchmark_data[industry]
    })
    st.dataframe(benchmark_df)

    if 'it_maturity_scores' in st.session_state:
        score_df = st.session_state['it_maturity_scores']
        compare_df = pd.merge(score_df, benchmark_df, on="Category")
        compare_df["Gap"] = compare_df["Score (%)"] - compare_df["Industry Average (%)"]
        st.subheader("📊 Your Score vs Industry Average")
        st.dataframe(compare_df)
        st.bar_chart(compare_df.set_index("Category")[["Score (%)", "Industry Average (%)"]])
    else:
        st.info("Complete the IT Assessment to see benchmark comparisons.")
elif section == "📊 Benchmarking Personas":
    st.title("📊 Benchmarking Personas")

    industry = st.selectbox("Select Industry", ["Healthcare", "Financial Services", "Retail", "Manufacturing", "Education", "Other"])
    company_size = st.selectbox("Select Company Size", ["< 500 employees", "500–5000", "> 5000"])
    user_role = st.radio("Your Role", ["CIO", "IT Director", "IT Ops", "Finance", "Other"])

    st.session_state.client_profile = {
        "industry": industry,
        "company_size": company_size,
        "user_role": user_role
    }

    st.subheader("📈 Benchmarked Averages (Mock Data)")
    bench_df = pd.DataFrame({
        "Category": ["Managed / Automated", "Standardized / Optimized", "Defined / Measured", "Reactive / Operational", "Survival, Ad-Hoc, Manual Legacy"],
        "Industry Average (%)": [82, 68, 63, 47, 30]
    })
    st.dataframe(bench_df)

    if 'it_assessment_scores' in st.session_state:
        score_df = st.session_state['it_maturity_scores']
        compare_df = pd.merge(score_df, bench_df, on="Category")
        compare_df["Gap"] = compare_df["Score (%)"] - compare_df["Industry Average (%)"]
        st.subheader("📊 Your Score vs Industry Average")
        st.dataframe(compare_df)
        st.bar_chart(compare_df.set_index("Category")[["Score (%)", "Industry Average (%)"]])
    else:
        st.info("Complete the IT Assessment to see benchmark comparisons.")

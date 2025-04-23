import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Revenue-at-Risk Model", layout="wide")
st.title("📈 Revenue-at-Risk Simulator")

# --- Inputs ---
st.sidebar.header("🔧 Model Inputs")

# Company Financials
total_revenue = st.sidebar.number_input("Total Annual Revenue ($M)", min_value=1, value=100, step=1) * 1_000_000
cyber_investment = st.sidebar.number_input("Annual Cybersecurity Investment ($K)", min_value=0, value=1000, step=100) * 1_000
bcdr_investment = st.sidebar.number_input("Annual BC/DR Investment ($K)", min_value=0, value=500, step=100) * 1_000

# Risk Exposure
risk_exposure_percent = st.sidebar.slider("% of Revenue at Risk without Protection", min_value=0, max_value=100, value=40)
risk_mitigation_effectiveness = st.sidebar.slider("Effectiveness of Cyber/BC Spend in Risk Reduction (%)", 0, 100, 75)

# --- Calculations ---
total_protective_investment = cyber_investment + bcdr_investment
revenue_at_risk = total_revenue * (risk_exposure_percent / 100)
avoided_loss = revenue_at_risk * (risk_mitigation_effectiveness / 100)
ropr = (avoided_loss - total_protective_investment) / total_protective_investment if total_protective_investment > 0 else 0

# --- Results ---
st.subheader("📊 Results Summary")

col1, col2, col3 = st.columns(3)
col1.metric("Revenue at Risk", f"${revenue_at_risk:,.0f}")
col2.metric("Avoided Revenue Loss", f"${avoided_loss:,.0f}")
col3.metric("ROPR (Return on Risk Prevention)", f"{ropr:.2f}x")

# --- Visualization ---
fig = go.Figure()
fig.add_trace(go.Bar(
    name="Risk Exposure",
    x=["Unprotected Revenue"],
    y=[revenue_at_risk],
    marker_color="red"
))
fig.add_trace(go.Bar(
    name="Avoided Loss",
    x=["Unprotected Revenue"],
    y=[avoided_loss],
    marker_color="green"
))
fig.update_layout(
    title="Impact of Cybersecurity & BC/DR Investments",
    yaxis_title="Revenue ($)",
    barmode="group",
    height=500
)
st.plotly_chart(fig, use_container_width=True)

# --- Explanation ---
st.markdown("""
### 🔬 How It Works
- **Revenue at Risk** is the portion of total revenue potentially lost in the event of cyberattacks or business interruptions.
- **Avoided Loss** is how much of that risk is mitigated by your cybersecurity and BC/DR investments.
- **ROPR** (Return on Risk Prevention) shows the financial value of those investments.
""")

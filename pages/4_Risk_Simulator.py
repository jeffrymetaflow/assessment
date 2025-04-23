import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.bootstrap import page_bootstrap

st.set_page_config(page_title="Revenue-at-Risk Model", layout="wide")
st.title("📈 Revenue-at-Risk Simulator")

page_bootstrap(current_page="Risk Simulator")  # Or "Risk Model", etc.

# --- Inputs ---
st.sidebar.header("🔧 Model Inputs")

# Pull from shared state or use default
total_revenue = st.session_state.get("revenue", 100_000_000)
cyber_investment = st.session_state.get("expense_by_category", {}).get("Cybersecurity", 1_000_000)
bcdr_investment = st.session_state.get("expense_by_category", {}).get("BC/DR", 500_000)

st.sidebar.info(f"Using Revenue: ${total_revenue:,.0f}")
st.sidebar.info(f"Using Cybersecurity Investment: ${cyber_investment:,.0f}")
st.sidebar.info(f"Using BC/DR Investment: ${bcdr_investment:,.0f}")

# Risk Exposure Inputs
risk_exposure_percent = st.sidebar.slider("% of Revenue at Risk without Protection", min_value=0, max_value=100, value=40)
risk_mitigation_effectiveness = st.sidebar.slider("Effectiveness of Cyber/BC Spend in Risk Reduction (%)", 0, 100, 75)

# --- Calculations ---
total_protective_investment = cyber_investment + bcdr_investment
revenue_at_risk = total_revenue * (risk_exposure_percent / 100)
avoided_loss = revenue_at_risk * (risk_mitigation_effectiveness / 100)
ropr = (avoided_loss - total_protective_investment) / total_protective_investment if total_protective_investment > 0 else 0

# Store in session for cross-tab use
st.session_state.risk_model = {
    "Revenue at Risk": revenue_at_risk,
    "Avoided Loss": avoided_loss,
    "ROPR": ropr,
    "Investments": {
        "Cybersecurity": cyber_investment,
        "BC/DR": bcdr_investment
    }
}

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

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Unified Executive Dashboard", layout="wide")
st.title("\U0001F4CA Unified Executive Dashboard")

# --- Sample Inputs (would eventually link to live modules) ---
st.sidebar.header("\U0001F4B0 High-Level Inputs")
revenue = st.sidebar.number_input("Annual Revenue ($M)", min_value=1, value=100) * 1_000_000
comparison_mode = st.sidebar.radio("Comparison Mode", ["Annual", "Quarterly"])
variance_threshold = st.sidebar.slider("Variance Threshold %", min_value=0, max_value=100, value=20)

# Simulated multi-period data
data = {
    "Period": [],
    "Hardware": [], "Software": [], "Personnel": [], "Maintenance": [], "Telecom": [], "Cybersecurity": [], "BC/DR": []
}
periods = ["2023 Q1", "2023 Q2", "2023 Q3", "2023 Q4", "2024 Q1", "2024 Q2"] if comparison_mode == "Quarterly" else ["2022", "2023", "2024"]

import random
for period in periods:
    data["Period"].append(period)
    for cat in list(data.keys())[1:]:
        data[cat].append(random.randint(100, 500) * 1000)

df = pd.DataFrame(data)
category_data = df.iloc[-1, 1:].to_dict()

risk_impact = {
    "Cybersecurity": {"Revenue Protected %": 25, "ROPR": 6.5},
    "BC/DR": {"Revenue Protected %": 18, "ROPR": 4.2}
}

# --- KPI Summary ---
st.subheader("\U0001F4C8 Key Metrics")
total_spend = sum(category_data.values())
it_ratio = total_spend / revenue * 100

col1, col2, col3 = st.columns(3)
col1.metric("Total IT Spend", f"${total_spend:,.0f}")
col2.metric("IT Spend / Revenue", f"{it_ratio:.2f}%")
col3.metric("Revenue at Risk (Protected)", f"{sum([v['Revenue Protected %'] for v in risk_impact.values()])}%")

# --- Multi-Period Line Chart with Variance Highlighting ---
st.subheader("\U0001F4C9 IT Spend Trends by Category")
fig_trend = go.Figure()
thresh = variance_threshold / 100
high_variance_categories = []
for cat in list(data.keys())[1:]:
    delta = abs((df[cat].iloc[-1] - df[cat].iloc[-2]) / df[cat].iloc[-2])
    color = 'firebrick' if delta > thresh else 'dodgerblue'
    if delta > thresh:
        high_variance_categories.append((cat, f"{delta*100:.1f}%"))
    fig_trend.add_trace(go.Scatter(
        x=df["Period"],
        y=df[cat],
        mode='lines+markers',
        name=cat,
        line=dict(color=color)
    ))
fig_trend.update_layout(yaxis_title="Spend ($)", height=450)
st.plotly_chart(fig_trend, use_container_width=True)

# --- Variance Alert Box ---
if high_variance_categories:
    st.warning("**High Variance Categories (>{}%)**:\n{}".format(
        variance_threshold,
        "\n".join([f"- {cat}: {val}" for cat, val in high_variance_categories])
    ))

# --- ROPR Line Chart ---
st.subheader("\U0001F4A1 Risk-Related ROI (ROPR)")
ropr_df = pd.DataFrame([(k, v['ROPR']) for k, v in risk_impact.items()], columns=['Category', 'ROPR'])
fig2 = go.Figure(go.Scatter(
    x=ropr_df['Category'],
    y=ropr_df['ROPR'],
    mode='lines+markers',
    marker=dict(color='seagreen'),
    line=dict(width=3)
))
fig2.update_layout(yaxis_title='Return on Risk Prevention (x)', height=400)
st.plotly_chart(fig2, use_container_width=True)

# --- Pie Chart: Revenue Protection Impact ---
st.subheader("\U0001F4B8 Revenue Protected by Category")
protection_df = pd.DataFrame([(k, v['Revenue Protected %']) for k, v in risk_impact.items()], columns=['Category', 'Protected %'])
fig3 = go.Figure(go.Pie(
    labels=protection_df['Category'],
    values=protection_df['Protected %'],
    textinfo='label+percent',
    hole=0.4
))
fig3.update_layout(height=400)
st.plotly_chart(fig3, use_container_width=True)

# --- Summary ---
st.markdown("""
### \U0001F4DD Summary
This executive dashboard provides a high-level view of IT financials, risk-adjusted investments, and revenue protection. It enables leadership to:
- Understand where IT spend is concentrated
- Track ROI on cybersecurity and continuity investments
- View trending IT financial data across multiple periods
- Highlight significant spend shifts (configurable threshold)
- Automatically surface categories exceeding variance limits
- Align technology strategy with margin and mission protection
""")

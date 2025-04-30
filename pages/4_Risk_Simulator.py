import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.bootstrap import page_bootstrap

st.set_page_config(page_title="Revenue at Risk Analysis", layout="wide")
st.title("💸 Revenue at Risk Simulator")

page_bootstrap(current_page="Revenue Risk")

# --------------------------
# Shared Revenue Input
# --------------------------
revenue = st.session_state.get("revenue", 5_000_000)
st.sidebar.header("📊 Base Revenue")
st.sidebar.info(f"Using Baseline Revenue: ${revenue:,.0f}")

# --------------------------
# Pull Component-Based Aggregates
# --------------------------
categories = ["Hardware", "Software", "Personnel", "Maintenance", "Telecom", "Cybersecurity", "BC/DR"]
controller = st.session_state.get("controller", None)

if controller:
    try:
        category_data = controller.get_category_aggregates()
    except Exception as e:
        st.warning(f"Failed to aggregate component data: {e}")
        category_data = {}
else:
    st.warning("No controller found in session state.")
    category_data = {}

# --------------------------
# Display Revenue Risk Table
# --------------------------
st.subheader("📋 Revenue Impact by IT Category")
risk_table = []
for cat in categories:
    spend = category_data.get(cat, {}).get("spend", 0)
    impact_pct = category_data.get(cat, {}).get("revenue_impact", 0) / 100
    revenue_risk = revenue * impact_pct
    risk_table.append((cat, spend, impact_pct * 100, revenue_risk))

risk_df = pd.DataFrame(risk_table, columns=["Category", "IT Spend", "% Revenue at Risk", "Revenue at Risk"])
st.dataframe(risk_df.style.format({
    "IT Spend": "${:,.0f}",
    "% Revenue at Risk": "{:.1f}%",
    "Revenue at Risk": "${:,.0f}"
}), use_container_width=True)

# --------------------------
# Visualize Revenue at Risk
# --------------------------
st.subheader("📉 Revenue at Risk by Category")
fig = go.Figure()
fig.add_trace(go.Bar(
    x=risk_df["Category"],
    y=risk_df["Revenue at Risk"],
    text=risk_df["Revenue at Risk"].apply(lambda x: f"${x:,.0f}"),
    textposition="outside",
    marker_color="indianred"
))
fig.update_layout(
    xaxis_title="Category",
    yaxis_title="Revenue at Risk ($)",
    title="Projected Revenue Exposure by IT Category",
    height=500
)
st.plotly_chart(fig, use_container_width=True)

# --------------------------
# Summary
# --------------------------
total_risk = risk_df["Revenue at Risk"].sum()
st.metric(label="💰 Total Revenue at Risk", value=f"${total_risk:,.0f}")

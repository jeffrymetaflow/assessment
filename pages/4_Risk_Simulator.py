import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Ensure controller is always initialized in session state
if "controller" not in st.session_state:
    from controller import ITRMController  # Adjust path if needed
    st.session_state.controller = ITRMController()

controller = st.session_state.controller
# Patch to safely run simulation avoiding missing keys
try:
    for c in controller.components:
        revenue_at_risk = (c.get("Revenue Impact %", 0) * c.get("Risk Score", 0)) / 100
        c["Revenue at Risk (%)"] = round(revenue_at_risk, 2)
    controller.simulation_results = pd.DataFrame(controller.components)
except Exception as e:
    st.error(f"Simulation error: {e}")

st.title("💸 Revenue at Risk Simulator")

# Display Simulation Table
st.subheader("📋 Component-Level Revenue at Risk")
st.dataframe(controller.simulation_results.style.format({"Revenue at Risk (%)": "{:.2f}%"}), use_container_width=True)

# Get and display category summary
category_risk = controller.get_category_risk_summary()
category_summary = pd.DataFrame([
    {
        "Category": cat,
        "Total Revenue at Risk (%)": round(data["total_risk"], 2),
        "# of Components": len(data["components"])
    }
    for cat, data in category_risk.items()
])

st.subheader("📊 Risk Summary by Category")
st.dataframe(category_summary.set_index("Category"), use_container_width=True)

# Chart visualization
fig = go.Figure()
fig.add_trace(go.Bar(
    x=category_summary["Category"],
    y=category_summary["Total Revenue at Risk (%)"],
    text=category_summary["Total Revenue at Risk (%)"].apply(lambda x: f"{x:.1f}%"),
    textposition="outside",
    marker_color="crimson"
))
fig.update_layout(
    title="Total Revenue at Risk by IT Category",
    xaxis_title="Category",
    yaxis_title="Revenue at Risk (%)",
    height=450
)
st.plotly_chart(fig, use_container_width=True)

# Show per-category components
st.subheader("🔍 Drill-Down: High-Risk Components by Category")
for cat, data in category_risk.items():
    with st.expander(f"{cat} - Total Risk: {round(data['total_risk'], 2)}%"):
        comp_df = pd.DataFrame(data["components"])
        st.dataframe(comp_df.style.format({
            "Revenue Impact %": "{:.1f}%",
            "Risk Score": "{:.0f}",
            "Revenue at Risk (%)": "{:.2f}%"
        }), use_container_width=True)

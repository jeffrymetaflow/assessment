import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Ensure controller is always initialized in session state
if "controller" not in st.session_state:
    from controller import ITRMController  # Adjust path if needed
    st.session_state.controller = ITRMController()

controller = st.session_state.controller

# Use category-level sliders as fallback if component-level fields are missing
category_impact_defaults = {
    cat: st.session_state.get(f"impact_slider_{cat}", 10)  # Default to 10%
    for cat in set(c.get("Category") for c in controller.components)
}

for c in controller.components:
    if "Revenue Impact %" not in c:
        c["Revenue Impact %"] = category_impact_defaults.get(c.get("Category"), 10)
    if "Risk Score" not in c:
        c["Risk Score"] = 5  # Default risk score if missing

# Assign missing Risk Score or Revenue Impact % values interactively
with st.expander("⚙️ Fix Missing Risk Data", expanded=False):
    needs_update = False
    for i, comp in enumerate(controller.components):
        if "Revenue Impact %" not in comp or "Risk Score" not in comp:
            st.markdown(f"**Component:** {comp.get('Name', 'Unnamed')}")
            comp["Revenue Impact %"] = st.slider(
                f"Revenue Impact % for {comp.get('Name', 'Unnamed')}",
                0, 100, 20, key=f"impact_{i}"
            )
            comp["Risk Score"] = st.slider(
                f"Risk Score for {comp.get('Name', 'Unnamed')}",
                0, 10, 5, key=f"risk_{i}"
            )
            needs_update = True
    if needs_update:
        if st.button("🔁 Rerun Simulation Now"):
            st.rerun()
        else:
            st.success("Missing values updated. Click 'Rerun Simulation Now' to refresh results.")

# Patch to safely run simulation avoiding missing keys
try:
    for c in controller.components:
        revenue_at_risk = (c.get("Revenue Impact %", 0) * c.get("Risk Score", 0)) / 100
        c["Revenue at Risk (%)"] = round(revenue_at_risk, 2)
        c["Revenue at Risk ($)"] = round((controller.get_baseline_revenue() or 0) * revenue_at_risk / 100, 2)
    controller.simulation_results = pd.DataFrame(controller.components)
except Exception as e:
    st.error(f"Simulation error: {e}")

st.title("💸 Revenue at Risk Simulator")

# --- Summary Metrics ---
category_risk = controller.get_category_risk_summary()
category_summary = pd.DataFrame([
    {
        "Category": cat,
        "Total Revenue at Risk ($)": round(sum(c.get("Revenue at Risk ($)", 0) for c in data["components"]), 2),
        "# of Components": len(data["components"])
    }
    for cat, data in category_risk.items()
])

# Patch for missing column
if category_summary.empty or "Total Revenue at Risk ($)" not in category_summary.columns:
    st.warning("⚠️ No valid 'Revenue at Risk' data found in components. Defaulting to 0s.")
    category_summary["Total Revenue at Risk ($)"] = 0.0
    category_summary["# of Components"] = 0

# Ensure correct revenue totals
total_risk = category_summary["Total Revenue at Risk ($)"].sum()
avg_risk = category_summary["Total Revenue at Risk ($)"].mean()
total_components = sum(len(data["components"]) for data in category_risk.values())

st.markdown(f"""
**🧮 Total Components:** `{total_components}`  
**🔥 Total Revenue at Risk:** `${total_risk:,.2f}`  
**📊 Average Category Risk:** `${avg_risk:,.2f}`
""")

# Component-Level Detail Behind Expander
with st.expander("📜 View Component-Level Revenue at Risk Table", expanded=False):
    st.dataframe(
        controller.simulation_results.style.format({
            "Revenue at Risk (%)": "{:.2f}%",
            "Revenue at Risk ($)": "${:,.2f}"
        }),
        use_container_width=True
    )

# Risk Summary by Category
st.subheader("📊 Risk Summary by Category")
st.dataframe(category_summary.set_index("Category").style.format({
    "Total Revenue at Risk ($)": "${:,.2f}"
}), use_container_width=True)

# Chart visualization
fig = go.Figure()
fig.add_trace(go.Bar(
    x=category_summary["Category"],
    y=category_summary["Total Revenue at Risk ($)"],
    text=category_summary["Total Revenue at Risk ($)"].apply(lambda x: f"${x:,.0f}"),
    textposition="outside",
    marker_color="crimson"
))
fig.update_layout(
    title="Total Revenue at Risk by IT Category",
    xaxis_title="Category",
    yaxis_title="Revenue at Risk ($)",
    height=450
)
st.plotly_chart(fig, use_container_width=True)

# Show per-category components
st.subheader("🔍 Drill-Down: High-Risk Components by Category")
for cat, data in category_risk.items():
    with st.expander(f"{cat} - Total Risk: ${round(sum(c.get('Revenue at Risk ($)', 0) for c in data['components']), 2):,.0f}", expanded=False):
        comp_df = pd.DataFrame(data["components"])
        st.dataframe(comp_df.style.format({
            "Revenue Impact %": "{:.1f}%",
            "Risk Score": "{:.0f}",
            "Revenue at Risk (%)": "{:.2f}%",
            "Revenue at Risk ($)": "${:,.2f}"
        }), use_container_width=True)

# 🔎 Optional Global High-Risk List
high_risk_threshold = 7
high_risk_components = [
    c for comps in category_risk.values()
    for c in comps["components"]
    if c.get("Risk Score", 0) >= high_risk_threshold
]

if high_risk_components:
    st.subheader(f"🚨 High-Risk Components (Score ≥ {high_risk_threshold})")
    high_risk_df = pd.DataFrame(high_risk_components)
    st.dataframe(high_risk_df.style.format({
        "Revenue Impact %": "{:.1f}%",
        "Risk Score": "{:.0f}",
        "Revenue at Risk (%)": "{:.2f}%",
        "Revenue at Risk ($)": "${:,.2f}"
    }), use_container_width=True)
else:
    st.info(f"No components above risk score threshold ({high_risk_threshold})")

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Ensure controller is initialized
if "controller" not in st.session_state:
    from controller import ITRMController
    st.session_state.controller = ITRMController()

controller = st.session_state.controller
baseline_revenue = controller.get_baseline_revenue() or 0
category_impact_map = controller.get_category_impact_percentages()

st.title("💸 Revenue at Risk Simulator")

# --- Calculate Baseline Revenue at Risk Per Category ---
category_baseline_risk = {}
for cat, impact_pct in category_impact_map.items():
    category_baseline_risk[cat] = baseline_revenue * (impact_pct / 100)

# --- Simulate Adjustment Sliders ---
st.subheader("⚙️ Simulate Revenue at Risk by Category")
simulated_risks = []
for cat in sorted(category_baseline_risk.keys()):
    base = category_baseline_risk[cat]
    adj = st.slider(f"{cat} Adjustment %", -100, 100, 0, key=f"risk_adj_{cat}")
    simulated = base * (1 + adj / 100)
    simulated_risks.append({
        "Category": cat,
        "Baseline Risk ($)": base,
        "Adjustment %": adj,
        "Adjusted Risk ($)": simulated
    })

sim_df = pd.DataFrame(simulated_risks)

# --- Summary KPIs ---
total_components = len(controller.components)
total_risk = sim_df["Adjusted Risk ($)"].sum()
avg_risk = sim_df["Adjusted Risk ($)"].mean()

st.markdown(f"""
**🧮 Total Components:** `{total_components}`  
**🔥 Total Simulated Revenue at Risk:** `${total_risk:,.2f}`  
**📊 Average Category Risk:** `${avg_risk:,.2f}`
""")

# --- Show Simulation Table ---
st.subheader("📊 Risk Simulation by Category")
st.dataframe(sim_df.set_index("Category").style.format({
    "Baseline Risk ($)": "${:,.2f}",
    "Adjustment %": "{:+.0f}%",
    "Adjusted Risk ($)": "${:,.2f}"
}), use_container_width=True)

# --- Visualization ---
fig = go.Figure()
fig.add_trace(go.Bar(
    x=sim_df["Category"],
    y=sim_df["Adjusted Risk ($)"],
    text=sim_df["Adjusted Risk ($)"].apply(lambda x: f"${x:,.0f}"),
    textposition="outside",
    marker_color="darkred"
))
fig.update_layout(
    title="Simulated Revenue at Risk by Category",
    xaxis_title="Category",
    yaxis_title="Adjusted Revenue at Risk ($)",
    height=460
)
st.plotly_chart(fig, use_container_width=True)

# --- Optional Debug/Details ---
with st.expander("🧾 View Category Risk Calculation Details"):
    st.dataframe(sim_df.style.format({
        "Baseline Risk ($)": "${:,.2f}",
        "Adjusted Risk ($)": "${:,.2f}"
    }), use_container_width=True)


import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.session_state import initialize_session
initialize_session()
from utils.auth import enforce_login
enforce_login()
from utils.bootstrap import page_bootstrap

st.title("💸 Revenue at Risk Simulator")

page_bootstrap(current_page="Risk Simulator")  # Or "Risk Model", etc.

# --- Retrieve Required Data ---
revenue = st.session_state.get("revenue", 0)

# Ensure controller is initialized and safely accessible
try:
    from controller.controller import ITRMController
    if "controller" not in st.session_state:
        st.session_state.controller = ITRMController()
    controller = st.session_state.controller

    # ✅ Always add the method to calculate category-level revenue impact %
    def get_category_impact_percentages():
        impact_totals = {}
        counts = {}
        for c in controller.components:
            cat = c.get("Category", "None")
            impact = c.get("Revenue Impact %", 0)
            if isinstance(impact, (int, float)):
                impact_totals[cat] = impact_totals.get(cat, 0) + impact
                counts[cat] = counts.get(cat, 0) + 1
        return {
            cat: round(impact_totals[cat] / counts[cat], 2)
            for cat in impact_totals
            if counts[cat] > 0
        }

    controller.get_category_impact_percentages = get_category_impact_percentages

    # ✅ Force populate session state if needed
    if not st.session_state.get("category_revenue_impact"):
        st.session_state["category_revenue_impact"] = controller.get_category_impact_percentages()

except Exception as e:
    st.error(f"❌ Failed to initialize controller: {e}")
    st.stop()

# 🔁 Baseline revenue fallback
baseline_revenue = st.session_state.get("revenue", 0)
if not baseline_revenue:
    baseline_revenue = getattr(controller, "baseline_revenue", 0)
    if not baseline_revenue:
        st.warning("⚠️ Baseline revenue not found. Please enter it on the main page.")

# Load category impact percentages
category_impact_map = st.session_state.get("category_revenue_impact", {})

# --- Calculate Baseline Risk Per Category ---
category_baseline_risk = {
    cat: baseline_revenue * (pct / 100)
    for cat, pct in category_impact_map.items()
    if isinstance(pct, (int, float))
}

# --- Simulate Adjustments ---
simulated_risks = []
adjustment_map = {}

if category_baseline_risk:
    st.subheader("⚙️ Simulate Revenue at Risk by Category")
    for cat in sorted(category_baseline_risk.keys(), key=str):
        base = category_baseline_risk[cat]
        adj = st.slider(f"{cat} Adjustment %", -100, 100, 0, key=f"risk_adj_{cat}")
        simulated = base * (1 + adj / 100)
        simulated_risks.append({
            "Category": cat,
            "Baseline Risk ($)": base,
            "Adjustment %": adj,
            "Adjusted Risk ($)": simulated
        })
        adjustment_map[cat] = adj
else:
    st.warning("⚠️ No category revenue impact data found. Please populate revenue impact % in the Component Mapping tab.")
    st.stop()

# --- Display Results ---
sim_df = pd.DataFrame(simulated_risks)

if not sim_df.empty and "Adjusted Risk ($)" in sim_df.columns:
    total_components = len(controller.components) if hasattr(controller, "components") else 0
    total_risk = sim_df["Adjusted Risk ($)"].sum()
    avg_risk = sim_df["Adjusted Risk ($)"].mean()

    st.markdown(f"""
    **🧮 Total Components:** `{total_components}`  
    **🔥 Total Simulated Revenue at Risk:** `${total_risk:,.2f}`  
    **📊 Average Category Risk:** `${avg_risk:,.2f}`
    """)

    st.subheader("📊 Risk Simulation by Category")
    st.dataframe(sim_df.set_index("Category").style.format({
        "Baseline Risk ($)": "${:,.2f}",
        "Adjustment %": "{:+.0f}%",
        "Adjusted Risk ($)": "${:,.2f}"
    }), use_container_width=True)

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

    with st.expander("🧾 View Category Risk Calculation Details"):
        st.dataframe(sim_df.style.format({
            "Baseline Risk ($)": "${:,.2f}",
            "Adjusted Risk ($)": "${:,.2f}"
        }), use_container_width=True)

    st.markdown("""
    ### 🧠 Logic Flow Behind This Simulation

    - **Baseline Revenue Source**: Retrieved from the Main Page setup or controller fallback.
    - **Component Mapping Page**: Revenue Impact % is averaged per category.
    - **Baseline Risk Calculation**: `Revenue × Average Revenue Impact % per Category`
    - **Adjustment Slider**: Lets user simulate increase/decrease in risk impact per category.
    - **Adjusted Risk Output**: `Baseline Risk × (1 + Adjustment %)`
    - **Visualization**: Table + Bar chart reflecting category risk before/after simulation.
    """)

else:
    st.info("No valid simulation data to display.")


from controller.supabase_controller import save_session_to_supabase

if st.button("💾 Save Project to Supabase"):
    save_session_to_supabase()

# Show last saved timestamp
if "project_data" in st.session_state:
    last_saved = st.session_state["project_data"].get("last_saved")
    if last_saved:
        st.caption(f"🕒 Last saved: {last_saved}")

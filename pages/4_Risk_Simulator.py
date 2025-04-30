import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Ensure controller is initialized and safely accessible
try:
    from controller.controller import ITRMController
    if "controller" not in st.session_state:
        st.session_state.controller = ITRMController()
    controller = st.session_state.controller

    # Patch: Dynamically calculate revenue impact % from components if missing
    if not hasattr(controller, "get_category_impact_percentages"):
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

except Exception as e:
    st.error(f"❌ Failed to initialize controller: {e}")
    st.stop()

try:
    baseline_revenue = controller.get_baseline_revenue() or 0
except Exception:
    baseline_revenue = 0
    st.warning("⚠️ Baseline revenue not found. Please enter it on the main page.")

# Safely get category impact percentages
try:
    category_impact_map = controller.get_category_impact_percentages()
except AttributeError:
    category_impact_map = {}
    st.warning("⚠️ Revenue impact percentages not available. Please assign impact values on the Component Mapping page.")

st.title("💸 Revenue at Risk Simulator")

# --- Calculate Baseline Revenue at Risk Per Category ---
category_baseline_risk = {}
for cat, impact_pct in category_impact_map.items():
    if isinstance(impact_pct, (int, float)):
        category_baseline_risk[cat] = baseline_revenue * (impact_pct / 100)

# --- Simulate Adjustment Sliders ---
simulated_risks = []
if category_baseline_risk:
    st.subheader("⚙️ Simulate Revenue at Risk by Category")
    if isinstance(category_baseline_risk, dict):
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
else:
    st.info("No category revenue impact data found. Please populate revenue impact % in the Component Mapping tab.")

# --- Render Simulation Results ---
sim_df = pd.DataFrame(simulated_risks)

if not sim_df.empty and "Adjusted Risk ($)" in sim_df.columns:
    try:
        total_components = len(controller.components)
    except Exception:
        total_components = 0

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
else:
    st.info("No valid simulation data to display.")

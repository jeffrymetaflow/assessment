import streamlit as st
import pandas as pd
from controller.controller import ITRMController
from utils.component_utils import init_session_state_from_components
from utils.bootstrap import page_bootstrap

page_bootstrap(current_page="Component_Mapping")  # Or "Risk Model", etc.

# 🔄 Ensure controller exists
if "controller" not in st.session_state:
    st.session_state.controller = ITRMController()

controller = st.session_state.controller
components = controller.get_components()

st.title("🧩 Component Mapping & Master Inputs")

# 🏛️ Global Master Inputs (used across app)
st.subheader("💼 Organization Financial Inputs")
st.session_state.revenue = st.number_input("Total Revenue ($)", value=5_000_000, step=100_000)

# 🧱 IT Component Builder
st.subheader("🧩 Add a New IT Component")

name = st.text_input("Component Name", key="mapping_comp_name_input")
category = st.selectbox("Category", [
    "Hardware", "Software", "Personnel", "Maintenance", "Telecom", "Cybersecurity", "BC/DR"
], key="mapping_comp_category")
spend = st.number_input("Annual Spend ($K)", min_value=0, value=100, step=10, key="mapping_comp_spend")
revenue_support = st.slider("% Revenue Supported", 0, 100, 20, key="mapping_revenue_slider")
risk_score = st.slider("Risk if Fails (0 = none, 100 = catastrophic)", 0, 100, 50, key="mapping_risk_slider")

# ➕ Add Component
if name and st.button("Add IT Component", key="mapping_add_button"):
    component = {
        "Name": name,
        "Category": category,
        "Spend": spend * 1000,
        "Revenue Impact %": revenue_support,
        "Risk Score": risk_score
    }
    controller.add_component(component)
    st.success(f"Component '{name}' added.")

# 🧠 Run simulation and sync session state
try:
    controller.run_simulation()
    init_session_state_from_components(controller)
except Exception as e:
    st.error(f"Simulation or sync error: {e}")

# 📊 Display Existing Components
st.subheader("📋 Current Component Inventory")
if components:
    df = pd.DataFrame(components)
    st.dataframe(df)

    # 📊 Aggregate Spend by Category
    if "Category" in df.columns and "Spend" in df.columns:
        agg_df = df.groupby("Category")["Spend"].sum().reset_index()
        st.session_state["category_spend_summary"] = agg_df  # persist to session state
        st.subheader("🔎 Aggregated Spend by Category")
        st.dataframe(agg_df)
else:
    st.info("No components added yet. Use the form above to get started.")
 

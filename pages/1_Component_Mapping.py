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
# Ensure all components have Revenue Impact % before running simulation
for c in controller.components:
    if "Revenue Impact %" not in c:
        cat = c.get("Category", "Unknown")
        c["Revenue Impact %"] = st.session_state.get("category_revenue_impact", {}).get(cat, 0)

# Ensure expense_growth keys are initialized
if "expense_growth" not in st.session_state:
    category_list = st.session_state.get("category_spend_summary", pd.DataFrame()).get("Category", pd.Series()).unique()
    st.session_state.expense_growth = {cat: [0.03, 0.03, 0.03] for cat in category_list}

# ✏️ Editable Expense Growth Rates by Category
st.subheader("📈 Adjust Expense Growth by Category")
for cat in st.session_state.expense_growth:
    current_val = st.session_state.expense_growth[cat][0]
    updated_val = st.number_input(f"{cat} Growth Rate (%)", min_value=0.0, max_value=1.0, value=current_val, step=0.01, key=f"growth_{cat}")
    st.session_state.expense_growth[cat] = [updated_val] * 3

try:
    controller.run_simulation()
    init_session_state_from_components(controller)
except Exception as e:
    import traceback
    st.error(f"Simulation or sync error: {e}")
    st.exception(traceback.format_exc())
    
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

        # 📈 Assign Revenue Impact % by Category
        category_impact = {}
        for _, row in agg_df.iterrows():
            cat = row["Category"]
            default_val = 20 if cat in ["Hardware", "Software"] else 10
            pct = st.slider(f"{cat} — Revenue Impact %", 0, 100, default_val, key=f"impact_{cat}")
            category_impact[cat] = pct

        st.session_state["category_revenue_impact"] = category_impact
else:
    st.info("No components added yet. Use the form above to get started.")


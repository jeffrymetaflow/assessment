import streamlit as st
import pandas as pd

controller = st.session_state.controller

st.title("🧩 Component Mapping")

name = st.text_input("Component Name", key="mapping_comp_name_input")
category = st.selectbox("Category", [
    "Hardware", "Software", "Personnel", "Maintenance", "Telecom", "Cybersecurity", "BC/DR"
], key="mapping_comp_category")
spend = st.number_input("Annual Spend ($K)", min_value=0, value=100, step=10, key="mapping_comp_spend")
revenue_support = st.slider("% Revenue Supported", 0, 100, 20, key="mapping_revenue_slider")
risk_score = st.slider("Risk if Fails (0 = none, 100 = catastrophic)", 0, 100, 50, key="mapping_risk_slider")

if name and st.button("Add IT Component", key="mapping_add_button"):
    component = {
        "Name": name,
        "Category": category,
        "Spend": spend * 1000,
        "Revenue Impact %": revenue_support,
        "Risk Score": risk_score
    }
    controller.add_component(component)

controller.run_simulation()

st.write("🧮 Total Components:", len(controller.components))
if controller.components:
    st.dataframe(pd.DataFrame(controller.components))

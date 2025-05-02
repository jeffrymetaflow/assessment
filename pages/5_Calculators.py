import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
from utils.bootstrap import page_bootstrap
from utils.session_state import initialize_session
initialize_session()

# ---------- Default Session State Initialization ----------
default_state = {
    "revenue": 1_000_000,
    "it_expense": 1_000_000,
    "revenue_growth": [5.0, 5.0, 5.0],
    "expense_growth": [3.0, 3.0, 3.0],
    "category_expenses_to_total": [0.1] * 5,
    "category_revenue_to_total": [0.05] * 5
}
for key, val in default_state.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ---------- Sidebar Navigation ----------
st.set_page_config(page_title="ITRM Dashboard", layout="wide")
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", [
    "🧠 Overview Summary",
    "⚙️ Inputs Setup",
    "📊 ITRM Calculator",
    "💰 ITRM Financial Summary",
])
client_name = st.sidebar.text_input("Client Name", placeholder="e.g., Acme Corp")

page_bootstrap(current_page="Calculators")  # Or "Risk Model", etc.

# ---------- Input Requirement Guard ----------
required_keys = ["revenue", "it_expense", "revenue_growth", "expense_growth"]
missing = [key for key in required_keys if key not in st.session_state]
if missing and section != "⚙️ Inputs Setup":
    st.warning("⚠️ Please configure your inputs in the '⚙️ Inputs Setup' tab first.")
    st.stop()

# ---------- Utility: Forecast Function ----------
def forecast_values(baseline, growth_rates):
    forecast = {}
    for i in range(3):
        year = f"Year {i+1}"
        if i == 0:
            forecast[year] = baseline
        else:
            prev = forecast[f"Year {i}"]
            growth_rate = growth_rates[i] if i < len(growth_rates) else 0
            forecast[year] = prev * (1 + growth_rate / 100)
    return forecast

# ---------- Inputs Setup ----------
if section == "⚙️ Inputs Setup":
    st.title("⚙️ Inputs Setup")

    controller = st.session_state.get("controller", None)
    if controller and hasattr(controller, "components"):
        st.write("📊 Pulled from Component Mapping:")
        st.dataframe(pd.DataFrame(controller.get_components()))
    if controller and hasattr(controller, "components"):
        df = pd.DataFrame(controller.components)
        default_revenue = st.session_state.get("revenue", 5_000_000)
        default_expense = df["Spend"].sum() if "Spend" in df.columns else 0

        category_totals = df.groupby("Category")["Spend"].sum() if "Category" in df.columns and "Spend" in df.columns else pd.Series(dtype=float)
        full_total = category_totals.sum()
        category_expenses_to_total = [category_totals.get(cat, 0) / full_total for cat in [
            "Hardware", "Software", "Personnel", "Maintenance", "Telecom"
        ]]
    else:
        default_revenue = st.session_state.revenue
        default_expense = st.session_state.it_expense
        category_expenses_to_total = st.session_state.category_expenses_to_total

    revenue = st.number_input("Revenue ($)", value=default_revenue)
    it_expense = st.number_input("IT Expense Baseline ($)", value=default_expense)

    categories = ["Hardware", "Software", "Personnel", "Maintenance", "Telecom"]
    category_expenses = [
        st.number_input(f"{cat} % of IT Expenses", value=category_expenses_to_total[i])
        for i, cat in enumerate(categories)
    ]
    category_revenue = [st.number_input(f"Category {i+1} % of Revenue", value=st.session_state.category_revenue_to_total[i]) for i in range(5)]

    revenue_growth = [st.number_input(f"Year {i+1} Revenue Growth (%)", value=st.session_state.revenue_growth[i]) for i in range(3)]
    expense_growth = [st.number_input(f"Year {i+1} Expense Growth (%)", value=st.session_state.expense_growth[i] if i < len(st.session_state.expense_growth) else 0) for i in range(3)]

    if st.button("Save Inputs"):
        st.session_state.update({
            "revenue": revenue,
            "it_expense": it_expense,
            "category_expenses_to_total": category_expenses,
            "category_revenue_to_total": category_revenue,
            "revenue_growth": revenue_growth,
            "expense_growth": expense_growth
        })
        st.success("Inputs saved successfully!")

# ---------- ITRM Calculator ----------
elif section == "📊 ITRM Calculator":
    st.title("📊 ITRM Multi-Year Calculator")

    revenue = forecast_values(st.session_state.revenue, st.session_state.revenue_growth)
    expenses = forecast_values(st.session_state.it_expense, st.session_state.expense_growth)

    st.session_state.revenue_input = revenue
    st.session_state.expense_input = expenses

    for year in revenue:
        st.markdown(f"**{year}: Revenue = ${revenue[year]:,.2f}, Expenses = ${expenses[year]:,.2f}**")

    itrm = {
        year: (expenses[year] / revenue[year]) * 100 if revenue[year] else 0
        for year in revenue
    }

    st.markdown("### ITRM Over Time")
    years = list(itrm.keys())
    values = list(itrm.values())
    fig, ax = plt.subplots()
    ax.plot(years, values, marker='o')
    ax.set_ylabel("IT Revenue Margin (%)")
    st.pyplot(fig)

# ---------- Financial Summary ----------
elif section == "💰 ITRM Financial Summary":
    st.title("💰 ITRM Financial Summary")

    revenue = st.session_state.revenue_input
    expenses = st.session_state.expense_input

    st.markdown("### Projected Revenue and Expenses")
    for year in revenue:
        st.markdown(f"**{year}**: Revenue = ${revenue[year]:,.2f}, Expenses = ${expenses[year]:,.2f}")

    itrm = {
        year: (expenses[year] / revenue[year]) * 100 if revenue[year] else 0
        for year in revenue
    }

    st.markdown("### ITRM by Year")
    for year in itrm:
        st.markdown(f"**{year} ITRM:** {itrm[year]:.2f}%")

    # Year-over-Year Revenue vs Expense Comparison
    st.markdown("### 📊 Year-over-Year Revenue vs. Expenses")
    years = list(revenue.keys())
    revenue_values = list(revenue.values())
    expense_values = list(expenses.values())

    fig2, ax2 = plt.subplots(figsize=(8, 6))
    ax2.bar(years, revenue_values, color='green', alpha=0.6, label='Revenue')
    ax2.bar(years, expense_values, color='red', alpha=0.6, label='Expenses')
    ax2.set_title("Year-over-Year Comparison")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Amount ($)")
    ax2.legend()
    st.pyplot(fig2)

    # Recommendations based on ITRM
    st.markdown("### 📌 Recommendations")
    for year in itrm:
        margin = itrm[year]
        if margin < 20:
            st.error(f"{year}: 🔴 Low Margin - Consider automation and reducing waste.")
        elif margin < 40:
            st.warning(f"{year}: 🟡 Medium Margin - Improve IT operations and cost control.")
        else:
            st.success(f"{year}: 🟢 Healthy Margin - Maintain and enhance automation.")

# ---------- Overview Summary ----------
elif section == "🧠 Overview Summary":
    st.title("🧠 IT Revenue Margin Strategy Summary")

    summary = f"""
    
st.markdown(summary)     
    
**Client Name:** {client_name or '<Client>'}

## Strategy Overview
- Optimize hybrid IT environments
- Improve cybersecurity maturity
- Reduce IT margin leakage via automation

## ITRM Next Steps
1. Conduct Workshops
2. Deploy Dashboards
3. Integrate Toolkits
"""




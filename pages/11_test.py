import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

# ---------- Sidebar Navigation ----------
st.set_page_config(page_title="ITRM Dashboard", layout="wide")
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", [
    "🧠 Overview Summary",
    "⚙️ Inputs Setup",
    "📊 ITRM Calculator",
    "💰 ITRM Financial Summary",
    "🔐 Cybersecurity Assessment"
])
client_name = st.sidebar.text_input("Client Name", placeholder="e.g., Acme Corp")

# ---------- Utility: Forecast Function ----------
def forecast_values(baseline, growth_rates):
    forecast = {}
    for i in range(3):
        year = f"Year {i+1}"
        if i == 0:
            forecast[year] = baseline
        else:
            prev = forecast[f"Year {i}"]
            forecast[year] = prev * (1 + growth_rates[i] / 100)
    return forecast

# ---------- Inputs Setup ----------
if section == "⚙️ Inputs Setup":
    st.title("⚙️ Inputs Setup")

    baseline_revenue = st.number_input("Baseline Revenue ($)", value=739_000_000)
    it_expense = st.number_input("IT Expense Baseline ($)", value=4_977_370)

    category_expenses = [st.number_input(f"Category {i+1} % of IT Expenses", value=0.1) for i in range(5)]
    category_revenue = [st.number_input(f"Category {i+1} % of Revenue", value=0.05) for i in range(5)]

    revenue_growth = [st.number_input(f"Year {i+1} Revenue Growth (%)", value=5.0) for i in range(3)]
    expense_growth = [st.number_input(f"Year {i+1} Expense Growth (%)", value=3.0) for i in range(3)]

    if st.button("Save Inputs"):
        st.session_state.update({
            "baseline_revenue": baseline_revenue,
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

    if 'baseline_revenue' not in st.session_state:
        st.warning("Please configure inputs in the Inputs Setup tab first.")
        st.stop()

    revenue = forecast_values(st.session_state.baseline_revenue, st.session_state.revenue_growth)
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

    if 'revenue_input' not in st.session_state or 'expense_input' not in st.session_state:
        st.warning("Run the ITRM Calculator first.")
        st.stop()

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
    st.markdown(summary)

# ---------- Cybersecurity Assessment ----------
elif section == "🔐 Cybersecurity Assessment":
    st.title("🔐 Cybersecurity Maturity Assessment")

    categories = [
        "Identify - Asset Mgmt", "Protect - Access Control", "Protect - Data Security",
        "Detect - Anomalies", "Respond - Planning", "Recover - Planning"
    ]

    scores = [st.slider(cat, 1, 5, 3, key=cat) for cat in categories]
    avg = sum(scores) / len(scores)
    st.session_state.cybersecurity_scores = dict(zip(categories, scores))

    st.markdown(f"**Overall Maturity Score:** {avg:.2f} / 5")
    if avg >= 4.5:
        st.success("Excellent cybersecurity posture.")
    elif avg >= 3:
        st.info("Moderate maturity. Consider improvements.")
    else:
        st.warning("Low maturity. Immediate enhancements needed.")


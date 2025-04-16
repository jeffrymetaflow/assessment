import streamlit as st

# Sidebar Navigation
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", ["🧠 Overview Summary", "📊 ITRM Calculator"])

# Shared Input
client_name = st.sidebar.text_input("Client Name", placeholder="e.g., Acme Corp")

# Overview Markdown Template
itrm_summary = """
**Title:** IT Revenue Margin (ITRM) Overview Summary  
**Subtitle:** Optimizing IT Efficiency with AI-Driven Solutions  
**Prepared by:** IT Strategy and Innovation Team

---

## Overview
This IT strategy session introduces an AI-driven IT optimization framework to help <Client Name> define a technology roadmap that reduces IT Revenue Margin, enhances IT resilience, and aligns IT investments with revenue growth. This approach provides end-to-end infrastructure, security, and data management strategies that support a dynamic, cost-effective IT environment.

---

## IT Strategy
Real-time IT ecosystem monitoring and automation ensures <Client Name>'s IT efficiency scales with business demand.

- Performance monitoring tools proactively optimize IT performance, reducing unnecessary resource consumption.  
- Security and compliance solutions help prevent risks that could impact IT revenue margins.  
- Systems management platforms automate IT workflows, reducing manual effort and operational costs.  

---

## IT Revenue Margin Calculation
By leveraging AI-driven infrastructure optimization tools, <Client Name> can dynamically adjust IT resource consumption.

- Monitoring and automation tools drive automated cost reduction in IT infrastructure.  
- Intelligent storage optimization reduces infrastructure costs significantly, directly improving IT Revenue Margin.  
- Comprehensive backup and recovery solutions ensure business continuity by minimizing downtime and disaster recovery costs.  

---

## ITRM Recommendations and Implementation
### Optimized IT Ecosystem Strategy

- Hybrid Cloud Optimization: Tools that dynamically shift workloads can reduce IT costs while maintaining high uptime.  
- Security and Compliance Enhancements: Solutions that mitigate risks and ensure regulatory compliance reduce overhead and increase system integrity.  
- IT Workflow Automation: Automation platforms streamline IT operations, enhancing productivity and efficiency.  

---

## Next Steps
1. Conduct ITRM Workshops – Offer CIOs and CTOs a structured assessment of their IT Revenue Margin and cost efficiency.  
2. Develop a Modular ITRM Dashboard – Create a scalable, subscription-based IT efficiency monitoring platform.  
3. Bundle IT Optimization Tools – Promote integration of performance monitoring, backup, automation, and security into a unified solution.  
4. Establish CIO Advisory Services – Use the ITRM deliverable as a lead-generation and strategic advisory tool.  

By adopting an AI-optimized IT revenue framework, <Client Name> can align IT operations with business performance, reduce waste, and ensure technology investments deliver maximum ROI.

**IT Revenue Margin – Driving Efficiency for Digital Transformation.**
"""

# Logic: Display selected section
if section == "🧠 Overview Summary":
    st.title("🧠 IT Revenue Margin Strategy Summary")
    if client_name:
        summary_display = itrm_summary.replace("<Client Name>", client_name)
    else:
        summary_display = itrm_summary
    st.markdown(summary_display, unsafe_allow_html=True)

elif section == "📊 ITRM Calculator":
    st.title("📊 ITRM Calculator")
    st.markdown("Data... Include cost inputs, margin graphs, and tool selection logic here.")

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("📊 ITRM Multi-Year Calculator")

# === Input section ===
st.markdown("### Enter Revenue Forecast and Expense Adjustment by Category")

revenue_input = {
    "Year 1": st.number_input("Year 1 Revenue ($)", value=812_900_000),
    "Year 2": st.number_input("Year 2 Revenue ($)", value=853_545_000),
    "Year 3": st.number_input("Year 3 Revenue ($)", value=913_293_150),
}

categories = ["Category 1", "Category 2", "Category 3", "Category 4", "Category 5"]
default_splits = [0.5, 0.2, 0.1, 0.15, 0.05]
default_changes = {
    "Year 1": [0.30, -0.20, -0.15, 0.10, 0.10],
    "Year 2": [0.05, -0.02, -0.20, 0.10, 0.05],
    "Year 3": [0.05, -0.02, -0.20, 0.10, 0.05],
}

expense_results = {}

st.markdown("---")

for year in ["Year 1", "Year 2", "Year 3"]:
    st.markdown(f"### {year} Category Settings")
    category_expenses = []
    revenue = revenue_input[year]

    for i, cat in enumerate(categories):
        col1, col2 = st.columns(2)
        with col1:
            split = st.number_input(f"{cat} Revenue % ({year})", min_value=0.0, max_value=1.0, value=default_splits[i], key=f"{year}_{cat}_split")
        with col2:
            change = st.number_input(f"{cat} Expense Change % ({year})", format="%.2f", value=default_changes[year][i], key=f"{year}_{cat}_change")

        expense = revenue * split * (1 + change)
        category_expenses.append(expense)

    total_expense = sum(category_expenses)
    itrm = (total_expense / revenue) * 100
    expense_results[year] = {"Total Expense": total_expense, "ITRM": itrm}

    st.success(f"**{year} Total Expense:** ${total_expense:,.2f}")
    st.info(f"**{year} IT Revenue Margin (ITRM):** {itrm:.2f}%")

st.markdown("---")

# === Chart section ===
st.markdown("### 📈 IT Revenue Margin Trend")
years = list(expense_results.keys())
itrms = [expense_results[y]["ITRM"] for y in years]

fig, ax = plt.subplots()
ax.plot(years, itrms, marker='o', linewidth=2)
ax.set_ylabel("IT Revenue Margin (%)")
ax.set_title("ITRM Over Time")
st.pyplot(fig)

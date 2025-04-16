import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# Sidebar Navigation
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", ["🧠 Overview Summary", "⚙️ Inputs Setup", "📊 ITRM Calculator"])
client_name = st.sidebar.text_input("Client Name", placeholder="e.g., Acme Corp")

# Overview Tab
if section == "🧠 Overview Summary":
    st.title("🧠 IT Revenue Margin Strategy Summary")
    itrm_summary = """...your summary content remains unchanged..."""
    summary_display = itrm_summary.replace("<Client Name>", client_name) if client_name else itrm_summary
    st.markdown(summary_display, unsafe_allow_html=True)

# Inputs Tab
elif section == "⚙️ Inputs Setup":
    if 'inputs' not in st.session_state:
        st.session_state.inputs = {
            'revenue_baseline': 739_000_000,
            'it_expense_baseline': 4_977_370,
            'category_revenue_split': [0.5, 0.2, 0.1, 0.15, 0.05],
            'category_expense_split': [0.25, 0.2, 0.1, 0.1, 0.35],
            'target_revenue_growth': [0.10, 0.05, 0.07],
            'target_expense_growth': [0.06, 0.03, 0.03]
        }

    st.title("⚙️ ITRM Inputs Setup")
    st.session_state.inputs['revenue_baseline'] = st.number_input("Baseline Revenue ($)", value=st.session_state.inputs['revenue_baseline'], key="inputs_revenue_baseline")
    st.session_state.inputs['it_expense_baseline'] = st.number_input("Baseline IT Expense ($)", value=st.session_state.inputs['it_expense_baseline'], key="inputs_it_expense_baseline")

    st.subheader("Application Category Splits")
    categories = ["Category 1", "Category 2", "Category 3", "Category 4", "Category 5"]
    revenue_splits, expense_splits = [], []
    for i, cat in enumerate(categories):
        col1, col2 = st.columns(2)
        with col1:
            rev = st.number_input(f"{cat} - % of Revenue", min_value=0.0, max_value=1.0, value=st.session_state.inputs['category_revenue_split'][i], key=f"inputs_{cat}_rev")
            revenue_splits.append(rev)
        with col2:
            exp = st.number_input(f"{cat} - % of Expense", min_value=0.0, max_value=1.0, value=st.session_state.inputs['category_expense_split'][i], key=f"inputs_{cat}_exp")
            expense_splits.append(exp)
    st.session_state.inputs['category_revenue_split'] = revenue_splits
    st.session_state.inputs['category_expense_split'] = expense_splits

    st.subheader("Target Revenue & Expense Growth")
    rev_growth, exp_growth = [], []
    for i, year in enumerate(["Year 1", "Year 2", "Year 3"]):
        col1, col2 = st.columns(2)
        with col1:
            rev = st.number_input(f"{year} Target Revenue Growth (%)", format="%.2f", value=st.session_state.inputs['target_revenue_growth'][i], key=f"inputs_{year}_rev_growth")
            rev_growth.append(rev)
        with col2:
            exp = st.number_input(f"{year} Target Expense Growth (%)", format="%.2f", value=st.session_state.inputs['target_expense_growth'][i], key=f"inputs_{year}_exp_growth")
            exp_growth.append(exp)
    st.session_state.inputs['target_revenue_growth'] = rev_growth
    st.session_state.inputs['target_expense_growth'] = exp_growth
    st.success("Inputs saved in session state. You can now use them in the calculator tab.")

# Calculator Tab
elif section == "📊 ITRM Calculator":
    st.title("📊 ITRM Multi-Year Calculator")
    if 'inputs' not in st.session_state:
        st.warning("Please configure inputs in the Inputs Setup tab first.")
        st.stop()

    inputs = st.session_state.inputs
    categories = ["Category 1", "Category 2", "Category 3", "Category 4", "Category 5"]
    revenue_input = {
        "Year 1": inputs['revenue_baseline'] * (1 + inputs['target_revenue_growth'][0]),
        "Year 2": inputs['revenue_baseline'] * (1 + inputs['target_revenue_growth'][1]),
        "Year 3": inputs['revenue_baseline'] * (1 + inputs['target_revenue_growth'][2]),
    }
    default_changes = {
        "Year 1": [0.30, -0.20, -0.15, 0.10, 0.10],
        "Year 2": [0.05, -0.02, -0.20, 0.10, 0.05],
        "Year 3": [0.05, -0.02, -0.20, 0.10, 0.05],
    }

    expense_results = {}
    for year in ["Year 1", "Year 2", "Year 3"]:
        st.markdown(f"#### {year} Adjustments")
        category_expenses, split_total = [], 0
        revenue = revenue_input[year]

        for i, cat in enumerate(categories):
            col1, col2 = st.columns(2)
            with col1:
                split = inputs['category_revenue_split'][i]
                st.markdown(f"{cat} Revenue %: **{split*100:.1f}%**")
            with col2:
                change = st.number_input(f"{cat} Expense Change % ({year})", format="%.2f", value=default_changes[year][i], key=f"calc_{year}_{cat}_change")
            split_total += split
            expense = revenue * split * (1 + change)
            category_expenses.append(expense)

        if abs(split_total - 1.0) > 0.001:
            st.error(f"{year} revenue splits do not total 100% (currently {split_total*100:.2f}%)")
            continue

        total_expense = sum(category_expenses)
        itrm = (total_expense / revenue) * 100
        expense_results[year] = {"Total Expense": total_expense, "ITRM": itrm}
        st.success(f"**{year} Total Expense:** ${total_expense:,.2f}")
        st.info(f"**{year} IT Revenue Margin (ITRM):** {itrm:.2f}%")

    if expense_results:
        st.markdown("---")
        st.subheader("📈 ITRM Trend")
        years = list(expense_results.keys())
        itrms = [expense_results[y]["ITRM"] for y in years]
        fig, ax = plt.subplots()
        ax.plot(years, itrms, marker='o', linewidth=2)
        ax.set_ylabel("IT Revenue Margin (%)")
        ax.set_title("ITRM Over Time")
        st.pyplot(fig)

        st.markdown("---")
        st.subheader("🧠 Summary Insights")
        first_year = years[0]
        last_year = years[-1]
        itrm_start = expense_results[first_year]["ITRM"]
        itrm_end = expense_results[last_year]["ITRM"]
        delta = itrm_start - itrm_end

        if delta > 0:
            st.success(f"✅ Over the modeled period, your IT Revenue Margin improved by {delta:.2f}%.")
            st.write("This indicates increased efficiency and optimization of IT resources relative to revenue growth.")
        elif delta < 0:
            st.warning(f"⚠️ IT Revenue Margin worsened by {-delta:.2f}%.")
            st.write("This may indicate IT cost growth outpacing revenue or ineffective optimization.")
        else:
            st.info("ℹ️ IT Revenue Margin remained consistent across the modeling period.")

        st.markdown("**Key Observations:**")
        st.markdown("- Monitor expense-heavy categories for targeted optimization.")
        st.markdown("- Validate whether revenue growth assumptions are realistic.")
        st.markdown("- Revisit automation or cloud strategies to reduce total IT spend.")

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="IT Forecast & Sensitivity Simulator", layout="wide")
st.title("📊 IT Spend Forecast & Sensitivity Model")

# 🧠 Pull revenue from session state
revenue = st.session_state.get("revenue", 5_000_000)
st.sidebar.header("📈 Master Financial Inputs")
st.sidebar.info(f"Using Baseline Revenue: ${revenue:,.0f}")

def category_input(label, default_growth, default_spend):
    col1, col2 = st.columns([2, 1])
    with col1:
        growth = st.slider(f"{label} Growth % per Year", -50, 100, default_growth)
    with col2:
        spend = st.number_input(f"Year 1 Spend ($K) - {label}", min_value=0, value=default_spend, step=10)
    return spend * 1000, growth

# 🔢 Define categories and defaults
categories = ["Hardware", "Software", "Personnel", "Maintenance", "Telecom", "Cybersecurity", "BC/DR"]
defaults = {
    "Hardware": (10, 300),
    "Software": (8, 250),
    "Personnel": (5, 400),
    "Maintenance": (2, 150),
    "Telecom": (4, 100),
    "Cybersecurity": (6, 180),
    "BC/DR": (3, 120)
}

# 📊 Collect forecast inputs
st.subheader("📊 Forecast Parameters")
data = {}
if "expense_growth" not in st.session_state:
    st.session_state.expense_growth = {}

expense_by_category = st.session_state.get("expense_by_category", {})

for cat in categories:
    # Pull fallback value from expense_by_category if available
    fallback_spend = int(expense_by_category.get(cat, defaults[cat][1] * 1000) / 1000)
    spend, growth = category_input(cat, defaults[cat][0], fallback_spend)
    data[cat] = {"Year 1": spend, "Growth %": growth}

    # Save to session state for reuse
    st.session_state.expense_growth[cat] = [growth / 100] * 3

# 📈 3-Year Forecast Logic
years = ["Year 1", "Year 2", "Year 3"]
forecast = {"Category": [], "Year": [], "Spend": []}

for cat, values in data.items():
    y1 = values["Year 1"]
    growth = values["Growth %"] / 100
    y2 = y1 * (1 + growth)
    y3 = y2 * (1 + growth)
    forecast["Category"].extend([cat] * 3)
    forecast["Year"].extend(years)
    forecast["Spend"].extend([y1, y2, y3])

forecast_df = pd.DataFrame(forecast)

# 📊 Show Forecast Table
st.subheader("📊 IT Spend Forecast Table")
styled_df = forecast_df.pivot(index="Category", columns="Year", values="Spend").style.format("${:,.0f}")
st.dataframe(styled_df, use_container_width=True)

# 📊 Stacked Forecast Chart
st.subheader("📊 IT Spend Over 3 Years")
fig = go.Figure()
for cat in categories:
    fig.add_trace(go.Bar(
        name=cat,
        x=years,
        y=forecast_df[forecast_df["Category"] == cat]["Spend"],
        text=forecast_df[forecast_df["Category"] == cat]["Spend"].apply(lambda x: f"${x:,.0f}"),
        textposition='auto'
    ))
fig.update_layout(
    barmode='stack',
    title='Projected IT Spend by Category',
    xaxis_title='Year',
    yaxis_title='Total Spend ($)',
    height=500
)
st.plotly_chart(fig, use_container_width=True)

# 📉 IT-to-Revenue Ratio Tracker
st.subheader("📉 IT-to-Revenue Ratio Over Time")
it_spend_by_year = forecast_df.groupby("Year")["Spend"].sum()
ratios = (it_spend_by_year / revenue).reset_index()
ratios.columns = ["Year", "IT Spend to Revenue Ratio"]

fig_ratio = go.Figure()
fig_ratio.add_trace(go.Scatter(
    x=ratios["Year"],
    y=ratios["IT Spend to Revenue Ratio"] * 100,
    mode='lines+markers',
    name='IT/Revenue %',
    marker=dict(color='blue')
))
fig_ratio.update_layout(
    title="IT Spend as % of Revenue",
    xaxis_title="Year",
    yaxis_title="IT Spend / Revenue (%)",
    height=400
)
st.plotly_chart(fig_ratio, use_container_width=True)

# 🌪️ Sensitivity Analysis
st.subheader("🌪️ Sensitivity Analysis")
if st.checkbox("Run Sensitivity Analysis"):
    min_factor = st.slider("Minimum Adjustment %", -50, 0, -20)
    max_factor = st.slider("Maximum Adjustment %", 0, 100, 20)

    sensitivity_results = []
    for cat in categories:
        base = data[cat]["Year 1"]
        min_val = base * (1 + min_factor / 100)
        max_val = base * (1 + max_factor / 100)
        sensitivity_results.append((cat, min_val, base, max_val))

    sens_df = pd.DataFrame(sensitivity_results, columns=["Category", "Min Spend", "Base Spend", "Max Spend"])
    st.dataframe(sens_df.set_index("Category").style.format("${:,.0f}"))

    # 📊 Sensitivity Range Chart
    fig2 = go.Figure()
    for _, row in sens_df.iterrows():
        fig2.add_trace(go.Bar(
            x=[row["Category"]],
            y=[row["Min Spend"]],
            name="Min",
            marker_color='lightblue',
            offsetgroup=0
        ))
        fig2.add_trace(go.Bar(
            x=[row["Category"]],
            y=[row["Base Spend"]],
            name="Base",
            marker_color='gray',
            offsetgroup=1
        ))
        fig2.add_trace(go.Bar(
            x=[row["Category"]],
            y=[row["Max Spend"]],
            name="Max",
            marker_color='salmon',
            offsetgroup=2
        ))
    fig2.update_layout(
        title="Sensitivity Ranges by IT Category",
        barmode='group',
        xaxis_title="Category",
        yaxis_title="Spend ($)",
        height=500
    )
    st.plotly_chart(fig2, use_container_width=True)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.bootstrap import page_bootstrap
from utils.session_state import initialize_session
initialize_session()

st.set_page_config(page_title="Unified Executive Dashboard", layout="wide")
st.title("\U0001F4CA Unified Executive Dashboard")

page_bootstrap(current_page="Executive Dashboard")  # Or "Risk Model", etc.

# --- Sidebar Inputs ---
st.sidebar.header("\U0001F4B0 High-Level Inputs")
revenue = st.sidebar.number_input("Annual Revenue ($M)", min_value=1, value=100) * 1_000_000
comparison_mode = st.sidebar.radio("Comparison Mode", ["Annual", "Quarterly"])
variance_threshold = st.sidebar.slider("Variance Threshold %", min_value=0, max_value=100, value=20)

# --- Simulated Data Generation ---
st.markdown("---")
st.markdown("## \U0001F4C8 Key Metrics")

# Simulated multi-period data
data = {
    "Period": [],
    "Hardware": [], "Software": [], "Personnel": [], "Maintenance": [], "Telecom": [], "Cybersecurity": [], "BC/DR": []
}
periods = ["2023 Q1", "2023 Q2", "2023 Q3", "2023 Q4", "2024 Q1", "2024 Q2"] if comparison_mode == "Quarterly" else ["2022", "2023", "2024"]

import random
for period in periods:
    data["Period"].append(period)
    for cat in list(data.keys())[1:]:
        data[cat].append(random.randint(100, 500) * 1000)

df = pd.DataFrame(data)
category_data = df.iloc[-1, 1:].to_dict()

risk_impact = {
    "Cybersecurity": {"Revenue Protected %": 25, "ROPR": 6.5},
    "BC/DR": {"Revenue Protected %": 18, "ROPR": 4.2}
}

# --- KPI Summary ---
total_spend = sum(category_data.values())
it_ratio = total_spend / revenue * 100

col1, col2, col3 = st.columns(3)
col1.metric("Total IT Spend", f"${total_spend:,.0f}")
col2.metric("IT Spend / Revenue", f"{it_ratio:.2f}%")
col3.metric("Revenue at Risk (Protected)", f"{sum([v['Revenue Protected %'] for v in risk_impact.values()])}%")

# --- Multi-Period Line Chart with Variance Highlighting ---
st.markdown("---")
st.markdown("## \U0001F4C9 IT Spend Trends by Category")
fig_trend = go.Figure()
thresh = variance_threshold / 100
high_variance_categories = []
for cat in list(data.keys())[1:]:
    delta = abs((df[cat].iloc[-1] - df[cat].iloc[-2]) / df[cat].iloc[-2])
    color = 'firebrick' if delta > thresh else 'dodgerblue'
    if delta > thresh:
        high_variance_categories.append((cat, f"{delta*100:.1f}%"))
    fig_trend.add_trace(go.Scatter(
        x=df["Period"],
        y=df[cat],
        mode='lines+markers',
        name=cat,
        line=dict(color=color)
    ))
fig_trend.update_layout(yaxis_title="Spend ($)", height=450)
st.plotly_chart(fig_trend, use_container_width=True)

# --- Variance Alert Box ---
if high_variance_categories:
    st.warning("**High Variance Categories (>{}%)**:\n{}".format(
        variance_threshold,
        "\n".join([f"- {cat}: {val}" for cat, val in high_variance_categories])
    ))

# --- Financial Summary ---
st.markdown("---")
st.markdown("## 💰 Financial Summary Snapshot")

if "category_spend_summary" in st.session_state and "category_revenue_impact" in st.session_state:
    cat_df = st.session_state["category_spend_summary"].copy()
    impact_map = st.session_state["category_revenue_impact"]

    cat_df["Revenue Impact %"] = cat_df["Category"].map(impact_map)
    cat_df["Revenue at Risk ($)"] = cat_df["Spend"] * (cat_df["Revenue Impact %"] / 100)

    st.dataframe(cat_df)
    st.metric("🔻 Total Revenue at Risk", f"${int(cat_df['Revenue at Risk ($)'].sum()):,}")
else:
    st.warning("Missing data: Please define revenue impact in Component Mapping first.")

# --- ROPR Line Chart ---
st.markdown("---")
st.markdown("## \U0001F4A1 Risk-Related ROI (ROPR)")
ropr_df = pd.DataFrame([(k, v['ROPR']) for k, v in risk_impact.items()], columns=['Category', 'ROPR'])
fig2 = go.Figure(go.Scatter(
    x=ropr_df['Category'],
    y=ropr_df['ROPR'],
    mode='lines+markers',
    marker=dict(color='seagreen'),
    line=dict(width=3)
))
fig2.update_layout(yaxis_title='Return on Risk Prevention (x)', height=400)
st.plotly_chart(fig2, use_container_width=True)

# --- Pie Chart: Revenue Protection Impact ---
st.markdown("---")
st.markdown("## \U0001F4B8 Revenue Protected by Category")
protection_df = pd.DataFrame([(k, v['Revenue Protected %']) for k, v in risk_impact.items()], columns=['Category', 'Protected %'])
fig3 = go.Figure(go.Pie(
    labels=protection_df['Category'],
    values=protection_df['Protected %'],
    textinfo='label+percent',
    hole=0.4
))
fig3.update_layout(height=400)
st.plotly_chart(fig3, use_container_width=True)

# --- Summary ---
st.markdown("---")
st.markdown("## \U0001F4DD Summary")
st.markdown("""
This executive dashboard provides a high-level view of IT financials, risk-adjusted investments, and revenue protection. It enables leadership to:
- Understand where IT spend is concentrated
- Track ROI on cybersecurity and continuity investments
- View trending IT financial data across multiple periods
- Highlight significant spend shifts (configurable threshold)
- Automatically surface categories exceeding variance limits
- Align technology strategy with margin and mission protection
""")

# ✅ Embedded AIOps Risk Scoring for Executive Dashboard
st.markdown("---")
st.markdown("## 🤖 AIOps Risk Scoring")

if "controller" in st.session_state:
    components = st.session_state.controller.get_components()
else:
    st.warning("No controller found. Please start from the Component Mapping page.")
    st.stop()

# Load revenue impact mapping
impact_map = st.session_state.get("category_revenue_impact", {})

if components:
    df = pd.DataFrame(components)
    if not df.empty:
        # Adjust risk score using Revenue Impact % from category level
        def adjust_score(row):
            base_score = row.get("Risk Score", 0)
            category = row.get("Category", "Unknown")
            impact_pct = impact_map.get(category, 0)
            return round(base_score * (1 + impact_pct / 100), 1)

        df["Adjusted Risk Score"] = df.apply(adjust_score, axis=1)

        st.markdown("### 📊 Adjusted Component Risk Scores")
        st.dataframe(df[["Name", "Category", "Spend", "Risk Score", "Adjusted Risk Score"]])

        avg_risk = df['Adjusted Risk Score'].mean()
        emoji = "🟢" if avg_risk < 4 else "🟡" if avg_risk < 7 else "🔴"
        st.metric("🔥 Average Adjusted Risk", f"{avg_risk:.1f} {emoji}")

        # 🔥 Risk Heatmap by Category
        st.markdown("### 🌡️ Risk Heatmap by Category")
        heatmap_df = df.groupby("Category")["Adjusted Risk Score"].mean().reset_index()
        import plotly.express as px
        fig4 = px.bar(heatmap_df, x="Category", y="Adjusted Risk Score", color="Adjusted Risk Score", height=400)
        fig4.update_layout(title="Average Adjusted Risk by Category")
        st.plotly_chart(fig4, use_container_width=True)

        # 📈 Spend vs. Adjusted Risk Scatter
        st.markdown("### 📉 Spend vs. Adjusted Risk")
        st.scatter_chart(df[["Spend", "Adjusted Risk Score"]])
    else:
        st.info("No components to score.")
else:
    st.info("No components loaded yet.")

# --- Forecast Chart from IT Spend Forecast Page ---
st.markdown("---")
st.markdown("## \U0001F4C5 Forecast Overview")
if "forecast_df" in st.session_state and "forecast_categories" in st.session_state:
    forecast_df = st.session_state["forecast_df"]
    categories = st.session_state["forecast_categories"]
    years = forecast_df["Year"].unique()

    fig = go.Figure()
    for cat in categories:
        df_cat = forecast_df[forecast_df["Category"] == cat]
        fig.add_trace(go.Bar(
            name=cat,
            x=df_cat["Year"],
            y=df_cat["Spend"],
            text=df_cat["Spend"].apply(lambda x: f"${x:,.0f}"),
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
else:
    st.info("No forecast data available. Please complete the Forecast module.")

# --- Inferred Strategic Recommendations ---
st.markdown("---")
st.markdown("## 🧭 Inferred Strategic Focus Areas")

recommendations = []

# 1. Cybersecurity Gaps
if "cybersecurity_scores" in st.session_state:
    df_cyber = pd.DataFrame.from_dict(st.session_state["cybersecurity_scores"], orient="index", columns=["Score"])
    weakest = df_cyber.sort_values("Score").head(2).index.tolist()
    for control in weakest:
        recommendations.append(f"Enhance cybersecurity control: **{control}**")

# 2. Assessment Gaps
if "assessment_answers" in st.session_state:
    low_sections = {}
    for k, v in st.session_state["assessment_answers"].items():
        section = k.split("_")[0]
        if v == "No":
            low_sections[section] = low_sections.get(section, 0) + 1
    for section, count in sorted(low_sections.items(), key=lambda x: -x[1])[:2]:
        recommendations.append(f"Address maturity issues in **{section}**")

# 3. Top Spend Areas
if "component_mapping" in st.session_state:
    df_comp = pd.DataFrame.from_dict(st.session_state["component_mapping"], orient="index")
    if "Spend" in df_comp.columns:
        top_spend = df_comp.groupby("Category")["Spend"].sum().sort_values(ascending=False).head(1)
        for cat in top_spend.index:
            recommendations.append(f"Evaluate optimization opportunities in high-spend area: **{cat}**")

# 4. Business Impact
if "category_revenue_impact" in st.session_state:
    impact = st.session_state["category_revenue_impact"]
    if isinstance(impact, dict):
        top_area = max(impact, key=impact.get)
        recommendations.append(f"Ensure resilience in high revenue-impact category: **{top_area}**")

# Render
if recommendations:
    for rec in recommendations:
        st.markdown(f"✅ {rec}")
else:
    st.info("No strategic insights currently inferred. Please complete assessments or mappings.")

# --- Cybersecurity Heatmap ---
st.markdown("---")
st.markdown("## \U0001F512 Cybersecurity Snapshot")
if "cybersecurity_scores" in st.session_state and st.session_state["cybersecurity_scores"]:
    df_cyber = pd.DataFrame.from_dict(st.session_state["cybersecurity_scores"], orient='index', columns=['Score'])
    df_cyber.index.name = "Control"
    df_cyber.reset_index(inplace=True)
    df_cyber["Score"] = df_cyber["Score"].astype(float)
    fig_bar = px.bar(
        df_cyber.sort_values(by="Score", ascending=True),
        x="Score",
        y="Control",
        orientation="h",
        color="Score",
        color_continuous_scale="RdBu",
        title="Cybersecurity Control Risk Scores",
        height=400
    )
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("No cybersecurity scores available yet.")
    
# --- Assessment Answers Summary ---
st.markdown("---")
st.markdown("## \U0001F4CB Assessment Highlights")
if "assessment_answers" in st.session_state and st.session_state["assessment_answers"]:
    answer_summary = {k.split("_")[0]: 0 for k in st.session_state["assessment_answers"]}
    for k, v in st.session_state["assessment_answers"].items():
        category = k.split("_")[0]
        if v == "Yes":
            answer_summary[category] += 1
    df_assess = pd.DataFrame(list(answer_summary.items()), columns=["Category", "Yes Count"])
    st.bar_chart(df_assess.set_index("Category"))
else:
    st.info("No assessment responses found.")

# --- Component Mapping Overview ---
st.markdown("---")
st.markdown("## \U0001F527 Component Mapping Overview")
if "component_mapping" in st.session_state and st.session_state["component_mapping"]:
    df_map = pd.DataFrame.from_dict(st.session_state["component_mapping"], orient='index')
    st.dataframe(df_map)
else:
    st.info("No component mapping data available.")

import streamlit as st
import openai
import os
import json
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from PIL import Image
import pytesseract
from utils.intent_classifier import classify_intent
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from utils.bootstrap import page_bootstrap
from utils.component_utils import get_unique_systems, get_components_by_system
from utils.session_state import initialize_session
from utils.auth import enforce_login
enforce_login()
from utils.component_utils import get_components_by_system
from utils.vector_index import answer_with_code_context

from typing import List

st.set_page_config(page_title="IT Architecture to Financial Mapping", layout="wide")
st.title("\U0001F5FA️ IT Architecture - Financial Impact Mapper")

page_bootstrap(current_page="Architecture")

# Ensure controller exists
if "controller" not in st.session_state:
    st.session_state.controller = {}

controller = st.session_state.controller

# Now safe to use controller
st.write("Architecture Page Loaded")


initialize_session()
controller = st.session_state.controller


def generate_ai_recommendations(components: List[dict], systems: List[str]) -> dict:
    recommendations = {}
    for system in systems:
        comps = get_components_by_system(system, components)
        comp_names = [comp.get("Name", "Unnamed") for comp in comps]
        system_summary = ", ".join(comp_names)

        prompt = (
            f"I'm working on improving an IT system named '{system}' composed of components: {system_summary}.\n"
            f"What architecture or modernization recommendations would you suggest for this system based on common patterns, performance improvements, and IT best practices?"
        )

        try:
            ai_response = answer_with_code_context(prompt)
        except Exception as e:
            ai_response = f"⚠️ Error calling AI: {e}"

        recommendations[system] = [ai_response]

    return recommendations


# --- AI Agent: Vendor Alternative Suggestion ---
def get_vendor_replacement_suggestion(component_name, category):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.3, openai_api_key=st.secrets["openai_api_key"])
    tools = [TavilySearchResults()]
    agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=False)

    prompt = (
        f"Act as an IT procurement strategist. For a component named '{component_name}' in category '{category}', "
        f"suggest 1-2 modern vendor alternatives and briefly explain the benefits. Include cost or lifecycle improvement if known."
    )

    try:
        result = agent.run(prompt)
    except Exception as e:
        result = f"(AI Suggestion failed: {e})"

    return result

# --- AI Scoring Logic ---
def score_component(metadata, weight_revenue=0.4, weight_risk=0.4, weight_cost=0.2):
    revenue_score = metadata["revenue_impact"] / 100
    risk_penalty = 1 - (metadata["risk_score"] / 100)
    cost_factor = 1 - (metadata["spend"] / 1000000)  # normalized cost
    score = round((weight_revenue * revenue_score) + (weight_risk * risk_penalty) + (weight_cost * cost_factor), 3)
    if score >= 0.75:
        recommendation = "✅ Healthy"
        color = "#C8E6C9"  # light green
    elif score >= 0.5:
        recommendation = "⚠️ Monitor"
        color = "#FFF9C4"  # light yellow
    else:
        recommendation = "❌ Optimize"
        color = "#FFCDD2"  # light red
    return score, recommendation, color

def initialize_state():
    if "components" not in st.session_state:
        st.session_state.components = []
    if "edges" not in st.session_state:
        st.session_state.edges = []
    if 'key' not in st.session_state:
        st.session_state['key'] = 'default_value'

if 'controller' not in st.session_state:
    st.session_state.controller = None  # Or initialize it with the appropriate value

if "components" not in st.session_state:
    st.session_state.components = []  # Initialize it as an empty list

controller = st.session_state.controller
components = controller.get_components()

if components:
    df = pd.DataFrame(components)
    st.dataframe(df)  # or continue building graph, tables, charts from df
else:
    st.warning("No components loaded. Please upload them on the Main page.")

def initialize_architecture_state():
    if "components" not in st.session_state:
        st.session_state.components = []
    if "edges" not in st.session_state:
        st.session_state.edges = []

initialize_architecture_state()

# --- Tabs ---
tabs = st.tabs(["Component Mapping", "Architecture Diagram", "External Import"])

# --- Component Mapping Tab --- 
with tabs[0]:
    st.header("📊 Define Components")

    controller = st.session_state.controller
    components = controller.get_components()
    df = pd.DataFrame(components) if components else pd.DataFrame(columns=["Name", "Category", "Spend", "Revenue Impact %", "Risk Score"])

    with st.expander("+ Add IT Component"):
        name = st.text_input("Component Name")
        category = st.selectbox("Category", ["Hardware", "Software", "Personnel", "Maintenance", "Telecom", "Cybersecurity", "BC/DR"])
        spend = st.number_input("Annual Spend ($)", min_value=0, value=100000, step=10000, format="%d")
        revenue_support = st.slider("% Revenue Supported", 0, 100, 20)
        risk_score = st.slider("Risk if Fails (0 = none, 100 = catastrophic)", 0, 100, 50)

        if st.button("Add Component"):
            if name.strip() == "":
                st.warning("Component name is required.")
            elif name in df["Name"].values:
                st.info(f"Component '{name}' already exists.")
            else:
                new_comp = {
                    "Name": name,
                    "Category": category,
                    "Spend": spend,
                    "Revenue Impact %": revenue_support,
                    "Risk Score": risk_score
                }
                components.append(new_comp)
                controller.set_components(components)
                st.success(f"Component '{name}' added.")

    with st.expander("+ Add Manual Link Between Components"):
        component_names = [c["Name"] for c in controller.get_components()]
        if component_names:
            source = st.selectbox("From Component", component_names, key="src")
            target = st.selectbox("To Component", component_names, key="tgt")

            if st.button("Add Link"):
                if source != target and (source, target) not in st.session_state.edges:
                    st.session_state.edges.append((source, target))
                else:
                    st.warning("Invalid or duplicate link.")

    # --- Filter by Category ---
    if controller.get_components():
        df = pd.DataFrame(controller.get_components())
        category_filter = st.multiselect("Filter by Category", df["Category"].unique().tolist(), default=df["Category"].unique().tolist())
        df = df[df["Category"].isin(category_filter)]

        st.subheader("📋 Component Mapping Table")
        st.dataframe(df)

def safe_score_row(row):
    try:
        enriched = enrich_component_metadata(row.to_dict())
        return pd.Series(score_component(enriched))
    except Exception as e:
        st.warning(f"Error scoring row {row.get('Name', '')}: {e}")
        return pd.Series([None, "❌ Error", "#FFFFFF"])
        
        # Updated scoring with fallback
        cat_df[["AI Score", "Recommendation", "Color"]] = cat_df.apply(safe_score_row, axis=1)
        
        st.subheader("🧠 Detailed Category Breakdown with Scores")
        categories = df["Category"].unique()
        for cat in categories:
            cat_df = df[df["Category"] == cat]
            cat_df = cat_df.copy()
            cat_df[["AI Score", "Recommendation", "Color"]] = cat_df.apply(
                lambda row: pd.Series(score_component(enrich_component_metadata(row.to_dict()))), axis=1
            )
            cat_df["Suggested Action"] = cat_df["Recommendation"].apply(lambda rec: (
                "Maintain current configuration" if "Healthy" in rec else
                "Flag for quarterly review" if "Monitor" in rec else
                "Review for vendor alternatives / consolidation opportunities"
            ))
            with st.expander(f"{cat} - {len(cat_df)} Components"):
                def highlight_row(row):
                    return ['background-color: {}'.format(row['Color']) if col == 'AI Score' else '' for col in row.index]
                st.dataframe(cat_df.style.apply(highlight_row, axis=1))
    else:
        st.info("Add components using the form above to get started.")

# --- Architecture Diagram Tab ---
with tabs[1]:
    if "category_spend_summary" in st.session_state and "category_revenue_impact" in st.session_state:
        components = controller.get_components()
        if not components:
            st.warning("No components found. Please define them in the Component Mapping page.")
            st.stop()

        df = pd.DataFrame(components)

        # Merge real 'Revenue at Risk ($)' from Executive Dashboard
        cat_summary = st.session_state["category_spend_summary"].copy()
        impact_map = st.session_state["category_revenue_impact"]
        cat_summary["Revenue Impact %"] = cat_summary["Category"].map(impact_map)
        cat_summary["Revenue at Risk ($)"] = cat_summary["Spend"] * (cat_summary["Revenue Impact %"] / 100)
        df = df.merge(cat_summary[["Category", "Revenue at Risk ($)"]], on="Category", how="left")

        # Build network graph
        G = nx.Graph()
        for _, row in df.iterrows():
            G.add_node(
                row["Name"],
                category=row["Category"],
                spend=row["Spend"],
                revenue=row["Revenue at Risk ($)"],
                risk=row["Risk Score"]
            )

        for edge in st.session_state.get("edges", []):
            G.add_edge(*edge)

        pos = nx.spring_layout(G, seed=42)
        node_x, node_y, node_text = [], [], []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            attr = G.nodes[node]
            node_text.append(
                f"{node}<br>Category: {attr['category']}<br>Spend: ${attr['spend']:,}"
                f"<br>Revenue at Risk: ${attr['revenue']:,.0f}<br>Risk: {attr['risk']}"
            )

        edge_x, edge_y = [], []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=edge_x, y=edge_y, line=dict(width=1, color='gray'), hoverinfo='none', mode='lines'))
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            textposition="top center",
            marker=dict(size=20, color=df["Risk Score"], colorscale='YlOrRd', showscale=True, colorbar=dict(title="Risk")),
            text=df["Name"], hovertext=node_text, hoverinfo='text'))

        fig.update_layout(title="\U0001F5FA️ Visual Architecture Layout", showlegend=False, height=600, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

        # Financial Summary
        st.subheader("💰 Financial Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total IT Spend", f"${df['Spend'].sum():,.0f}")
        col2.metric("Total Revenue at Risk", f"${df['Revenue at Risk ($)'].sum():,.0f}")
        col3.metric("Avg. Risk Score", f"{df['Risk Score'].mean():.1f}")
    else:
        st.warning("Missing Executive Summary data. Please run the Financial Summary tab first.")

# --- Roadmap Recommendations Tab ---
st.subheader("🛣️ AI-Powered Roadmap Recommendations")
if st.session_state.components:
    df = pd.DataFrame(st.session_state.components)
    df = df.copy()
    df[["AI Score", "Recommendation", "Color"]] = df.apply(
        lambda row: pd.Series(score_component(enrich_component_metadata(row.to_dict()))), axis=1
    )
    df["Suggested Action"] = df["Recommendation"].apply(lambda rec: (
        "Maintain current configuration" if "Healthy" in rec else
        "Flag for quarterly review" if "Monitor" in rec else
        "Review for vendor alternatives / consolidation opportunities"
    ))

    st.markdown("### 🔍 Priority Actions")
    low_score_df = df[df["Recommendation"].str.contains("Optimize")].sort_values("AI Score")
    if not low_score_df.empty:
        st.write("Below are the most critical components to address:")
        for i, row in low_score_df.iterrows():
            st.markdown(f"**{row['Name']}** ({row['Category']})")
            st.markdown(f"- Spend: ${row['Spend']:,.0f}")
            st.markdown(f"- Risk Score: {row['Risk Score']} | AI Score: {row['AI Score']}")
            st.markdown(f"- Suggested Action: _{row['Suggested Action']}_")
            if i < 3:
                if f"ai_{row['Name']}" not in st.session_state:
                    st.session_state[f"ai_{row['Name']}"] = get_vendor_replacement_suggestion(row['Name'], row['Category'])
                st.markdown(f"- **AI Suggested Vendors:** {st.session_state[f'ai_{row['Name']}']}")
            else:
                if st.button(f"Suggest Alternatives for {row['Name']}", key=f"btn_{i}"):
                    st.session_state[f"ai_{row['Name']}"] = get_vendor_replacement_suggestion(row['Name'], row['Category'])
                if f"ai_{row['Name']}" in st.session_state:
                    st.markdown(f"- **AI Suggested Vendors:** {st.session_state[f'ai_{row['Name']}']}")
    else:
        st.success("No critical components flagged for optimization.")

    st.markdown("### ⬇️ Export Plan")
    csv = low_score_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Optimization Roadmap (CSV)", csv, "optimization_roadmap.csv", "text/csv")

    st.markdown("### 📊 Gantt Chart: Prioritized Remediation Timeline")
    low_score_df = low_score_df.copy()
    low_score_df["Priority Index"] = low_score_df["Spend"] / (low_score_df["Risk Score"] + 1)  # Prevent divide-by-zero
    low_score_df = low_score_df.sort_values("Priority Index", ascending=False)
    low_score_df["Start"] = pd.to_datetime("today")
    low_score_df["Finish"] = low_score_df["Start"] + pd.to_timedelta((low_score_df["Priority Index"] * 2).astype(int), unit='D')

    gantt_fig = go.Figure()
    for _, row in low_score_df.iterrows():
        gantt_fig.add_trace(go.Bar(
            x=[(row["Finish"] - row["Start"]).days],
            y=[row["Name"]],
            base=row["Start"],
            orientation='h',
            marker=dict(color='crimson' if row["Risk Score"] > 70 else 'gold' if row["Risk Score"] > 40 else 'lightgreen'),
            name=row["Category"],
            hovertext=f"Spend: ${row['Spend']:,.0f}<br>Risk: {row['Risk Score']}<br>Priority: {row['Priority Index']:.2f}"
        ))

    gantt_fig.update_layout(
        title="Remediation Timeline by Priority (Gantt View)",
        barmode='stack',
        xaxis_title="Date",
        yaxis_title="Component",
        height=600,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    st.plotly_chart(gantt_fig, use_container_width=True)

st.markdown("## 🧠 AI-Powered Roadmap Recommendations")

if st.button("Get Recommendations"):
    if "components" not in st.session_state:
        st.warning("No components loaded. Please define architecture components first.")
    else:
        systems = get_unique_systems(st.session_state["components"])
        recommendations = generate_ai_recommendations(st.session_state["components"], systems)
        st.subheader("🔍 Recommendations")
        for system, recs in recommendations.items():
            st.markdown(f"### {system}")
            for r in recs:
                st.markdown(f"- {r}")

# --- Simulation Tab ---
st.subheader("🧪 Simulation Mode: Live Feed Preview")
st.markdown("Use this simulator to preview how real-time architecture updates might flow into the system from an external AIOps or CMDB API.")

api_response_mock = {
    "components": [
        {"Name": "Simulated Switch X930", "Category": "Hardware", "Spend": 125000, "Revenue Impact %": 12, "Risk Score": 66},
        {"Name": "Simulated WAF Cluster", "Category": "Cybersecurity", "Spend": 89000, "Revenue Impact %": 18, "Risk Score": 72},
        {"Name": "Simulated HRIS System", "Category": "Software", "Spend": 210000, "Revenue Impact %": 25, "Risk Score": 55}
    ]
}

if st.button("Inject Simulated API Feed"):
    st.session_state.components.extend(api_response_mock["components"])
    st.success("Simulated data injected into the component mapping.")

with st.expander("View Mock API Payload"):
    st.code(json.dumps(api_response_mock, indent=2), language='json')

# --- External Import Tab ---
with tabs[2]:
    st.subheader("\U0001F4C2 Upload External Architecture (Visio / AIOps")
    visio_file = st.file_uploader("Upload Visio Diagram (.vsdx)", type="vsdx")
    if visio_file:
        st.info("(Placeholder) Parsing of Visio files will be added here.")
        st.write("File name:", visio_file.name)

    st.markdown("---")
    st.subheader("\U0001F916 Optional AIOps Integration")
    st.text_input("Enter AIOps API URL", key="aiops_url")
    st.button("Test Connection", key="test_aiops")

if st.sidebar.checkbox("Show session state (dev only)"):
    st.write(st.session_state)






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

from controller.controller import ITRMController
from utils.bootstrap import page_bootstrap

# --- Sample Component Metadata for AI Scoring ---
def enrich_component_metadata(component):
    metadata = {
        "name": component["Name"],
        "category": component["Category"],
        "spend": component["Spend"],
        "revenue_impact": component["Revenue Impact %"],
        "risk_score": component["Risk Score"],
        "lifespan": 3,  # placeholder in years
        "alternatives": ["AltA", "AltB"],  # placeholder
        "vendor": "VendorX",  # placeholder
    }
    return metadata

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

# --- Controller Initialization ---
if "controller" not in st.session_state:
    st.session_state.controller = ITRMController()

def initialize_state():
    if "components" not in st.session_state:
        st.session_state.components = []
    if "edges" not in st.session_state:
        st.session_state.edges = []
    if 'key' not in st.session_state:
        st.session_state['key'] = 'default_value'

initialize_state()
controller = st.session_state.controller

st.set_page_config(page_title="IT Architecture to Financial Mapping", layout="wide")
st.title("\U0001F5FA️ IT Architecture - Financial Impact Mapper")

page_bootstrap(current_page="Architecture")

# --- Tabs ---
tabs = st.tabs(["Component Mapping", "Architecture Diagram", "External Import"])

# --- Component Mapping Tab ---
with tabs[0]:
    st.header("\U0001F4C8 Define Components")
    with st.expander("+ Add IT Component"):
        name = st.text_input("Component Name")
        category = st.selectbox("Category", ["Hardware", "Software", "Personnel", "Maintenance", "Telecom", "Cybersecurity", "BC/DR"])
        spend = st.number_input("Annual Spend ($)", min_value=0, value=100000, step=10000, format="%d")
        revenue_support = st.slider("% Revenue Supported", 0, 100, 20)
        risk_score = st.slider("Risk if Fails (0 = none, 100 = catastrophic)", 0, 100, 50)

        if st.button("Add Component"):
            st.session_state.components.append({
                "Name": name,
                "Category": category,
                "Spend": spend,
                "Revenue Impact %": revenue_support,
                "Risk Score": risk_score
            })

    with st.expander("+ Add Manual Link Between Components"):
        component_names = [c["Name"] for c in st.session_state.components]
        if component_names:
            source = st.selectbox("From Component", component_names, key="src")
            target = st.selectbox("To Component", component_names, key="tgt")

            if st.button("Add Link"):
                if source != target and (source, target) not in st.session_state.edges:
                    st.session_state.edges.append((source, target))
                else:
                    st.warning("Invalid or duplicate link.")

    # --- Filter by Category ---
    if st.session_state.components:
        df = pd.DataFrame(st.session_state.components)
        category_filter = st.multiselect("Filter by Category", df["Category"].unique().tolist(), default=df["Category"].unique().tolist())
        df = df[df["Category"].isin(category_filter)]

        st.subheader("\U0001F4CA Component Mapping Table")
        st.dataframe(df)

        st.subheader("\U0001F52C Detailed Category Breakdown with Scores")
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
cat_df["Suggested Action"] = cat_df["Recommendation"].apply(lambda rec: (
    "Maintain current configuration" if "Healthy" in rec else
    "Flag for quarterly review" if "Monitor" in rec else
    "Review for vendor alternatives / consolidation opportunities"
))
            with st.expander(f"{cat} - {len(cat_df)} Components"):
                st.dataframe(
                    cat_df.style.apply(lambda x: [f'background-color: {c}' for c in x["Color"]], axis=1, subset=['AI Score'])
                )
    else:
        st.info("Add components using the form above to get started.")

# --- Architecture Diagram Tab ---
with tabs[1]:
    if st.session_state.components:
        st.subheader("\U0001F4D0 Architecture Dependency Map")
        df = pd.DataFrame(st.session_state.components)

        G = nx.Graph()
        for _, row in df.iterrows():
            G.add_node(row['Name'], category=row['Category'], spend=row['Spend'], revenue=row['Revenue Impact %'], risk=row['Risk Score'])

        for edge in st.session_state.edges:
            G.add_edge(*edge)

        pos = nx.spring_layout(G, seed=42)
        node_x, node_y, node_text = [], [], []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            attr = G.nodes[node]
            node_text.append(f"{node}<br>Category: {attr['category']}<br>Spend: ${attr['spend']:,}<br>Revenue Support: {attr['revenue']}%<br>Risk: {attr['risk']}")

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
            marker=dict(size=20, color=df['Risk Score'], colorscale='YlOrRd', showscale=True, colorbar=dict(title="Risk")),
            text=df['Name'], hovertext=node_text, hoverinfo='text'))

        fig.update_layout(title="\U0001F5FA️ Visual Architecture Layout", showlegend=False, height=600, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("\U0001F4B0 Financial Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total IT Spend", f"${df['Spend'].sum():,.0f}")
        col2.metric("Avg. Revenue Supported", f"{df['Revenue Impact %'].mean():.1f}%")
        col3.metric("Avg. Risk Score", f"{df['Risk Score'].mean():.1f}")
    else:
        st.info("Add components in the first tab to generate an architecture diagram.")

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

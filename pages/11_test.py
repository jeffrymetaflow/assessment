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

# 🔁 Initialize shared controller only once
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

    if st.session_state.components:
        df = pd.DataFrame(st.session_state.components)
        st.subheader("\U0001F4CA Component Mapping Table")
        st.dataframe(df)
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

# Cleaned up duplicate inputs and isolated initialization
st.write(st.session_state)

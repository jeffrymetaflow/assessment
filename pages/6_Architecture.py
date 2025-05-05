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
from utils.session_state import initialize_session
from utils.auth import enforce_login
enforce_login()

initialize_session()
controller = st.session_state.controller

st.set_page_config(page_title="IT Architecture to Financial Mapping", layout="wide")
st.title("\U0001F5FA️ IT Architecture - Financial Impact Mapper")

page_bootstrap(current_page="Architecture")


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
            with st.expander(f"{cat} - {len(cat_df)} Components"):
                def highlight_row(row):
                    return ['background-color: {}'.format(row['Color']) if col == 'AI Score' else '' for col in row.index]
                st.dataframe(cat_df.style.apply(highlight_row, axis=1))
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






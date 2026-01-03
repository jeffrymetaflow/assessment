import plotly.express as px
import plotly.graph_objects as go

def chart_score_distribution(df):
    return px.histogram(df, x="score", nbins=10,
        title="AI Assessment Score Distribution", color="category")

def chart_confidence_trend(df):
    return px.line(df, x="timestamp", y="confidence",
        color="category", markers=True,
        title="Model Confidence Over Time")

def chart_radar_metrics(metrics):
    categories = list(metrics.keys())
    values = list(metrics.values())
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                      showlegend=False,
                      title="AI Capability Radar")
    return fig

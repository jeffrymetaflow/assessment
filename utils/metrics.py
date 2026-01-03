import numpy as np

def compute_summary_metrics(df):
    return {
        "avg_score": df["score"].mean(),
        "median_confidence": df["confidence"].median(),
        "risk_average": df["risk"].mean() if "risk" in df else np.nan
    }

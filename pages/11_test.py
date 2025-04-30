import streamlit as st
import pandas as pd

st.title("🤖 AIOps Risk Scoring")

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

        st.subheader("📊 Adjusted Component Risk Scores")
        st.dataframe(df[["Name", "Category", "Spend", "Risk Score", "Adjusted Risk Score"]])

        st.metric("🔥 Average Adjusted Risk", f"{df['Adjusted Risk Score'].mean():.1f}")

        # 🔥 Risk Heatmap by Category
        st.subheader("🌡️ Risk Heatmap by Category")
        heatmap_df = df.groupby("Category")["Adjusted Risk Score"].mean().reset_index()
        st.bar_chart(heatmap_df.set_index("Category"))

        # 📈 Spend vs. Adjusted Risk Scatter
        st.subheader("📉 Spend vs. Adjusted Risk")
        st.scatter_chart(df[["Spend", "Adjusted Risk Score"]]):.1f}")
    else:
        st.info("No components to score.")
else:
    st.info("No components loaded yet.")

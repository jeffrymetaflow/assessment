# --- SIDEBAR ---
with st.sidebar:
    st.image("logo.png", width=140)  # Optional: Add your company or product logo

    st.markdown("## 🧾 Project Summary")
    st.markdown(f"**Client:** {st.session_state.get('client_name', '-')}")
    st.markdown(f"**Project:** {st.session_state.get('project_name', '-')}")
    st.markdown(f"**Revenue:** ${st.session_state.get('project_revenue', 0):,.0f}")

    st.markdown("---")

    st.markdown("## 💾 Session Controls")

    # Export session as downloadable JSON
    session_data = {k: v for k, v in st.session_state.items() if not k.startswith('_')}
    json_str = json.dumps(session_data, default=str)
    st.download_button(
        label="⬇️ Export Session",
        data=json_str,
        file_name="ITRM-session.json",
        mime="application/json"
    )

    # Upload session to restore state
    uploaded_file = st.file_uploader("⬆️ Import Session", type="json")
    if uploaded_file is not None:
        uploaded_state = json.load(uploaded_file)
        for k, v in uploaded_state.items():
            st.session_state[k] = v
        st.success("✅ Session loaded!")

    if st.button("🧹 Reset Session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown("---")

    if "recommendations" in st.session_state and st.session_state["recommendations"]:
        st.markdown("## ✅ Recommended Actions")
        for rec in st.session_state["recommendations"]:
            st.markdown(f"- {rec}")

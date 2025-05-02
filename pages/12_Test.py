# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 📊 Session Info")
    st.write(f"Client: {st.session_state.get('client_name', '-')}")
    st.write(f"Project: {st.session_state.get('project_name', '-')}")
    st.write(f"Revenue: {st.session_state.get('project_revenue', '-')}")

# Export session as downloadable JSON
session_data = {k: v for k, v in st.session_state.items() if not k.startswith('_')}
json_str = json.dumps(session_data, default=str)
st.sidebar.download_button(
    label="💾 Export Session",
    data=json_str,
    file_name="ITRM-session.json",
    mime="application/json"
)

# Upload session to restore state
uploaded_file = st.sidebar.file_uploader("🔁 Import Session", type="json")
if uploaded_file is not None:
    uploaded_state = json.load(uploaded_file)
    for k, v in uploaded_state.items():
        st.session_state[k] = v
    st.sidebar.success("✅ Session loaded!")

if st.sidebar.button("🧹 Reset Session"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()


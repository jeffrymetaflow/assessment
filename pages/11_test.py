import streamlit as st

# Static questionnaire definition
questionnaire = [
    {
        "section": "Managed / Automated",
        "questions": [
            "Failover between sites",
            "Software Intelligence",
            "Converged Infrastructure standardization",
            "Replication",
            "User Defined Recovery"
        ]
    },
    {
        "section": "Governance / Policy",
        "questions": [
            "Formal incident response policy exists",
            "Quarterly risk assessments are conducted",
            "Compliance framework is implemented (e.g., NIST, ISO)"
        ]
    }
]

# Display title
st.title("\U0001F9E0 IT Maturity Assessment Tool")
st.markdown("""
Welcome to the interactive IT Maturity Assessment. Please answer the following questions based on your current IT environment. Your responses will be used to calculate a maturity score across several technology domains.
""")

# Display form
with st.form("maturity_form"):
    responses = {}
    for block in questionnaire:
        st.subheader(block["section"])
        for q in block["questions"]:
            responses[q] = st.radio(q, ["Yes", "No"], key=q)
    submitted = st.form_submit_button("Submit")

if submitted:
    st.success("✅ Responses submitted successfully!")
    st.write(responses)

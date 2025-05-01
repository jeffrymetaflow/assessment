import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# Full Cybersecurity Maturity Assessment Questions
questionnaire = [
    {
        "section": "Identity - Survival, Ad-Hoc, Manual Legacy",
        "questions": [
            "Does your organization maintain an inventory of all authorized and unauthorized devices connected to your network?",
            "Do you have an inventory of all authorized and unauthorized software within your organization?",
            "Have you established an asset management process that tracks the lifecycle of devices and software?",
            "Does your organization have a documented policy for identity and access management?"
        ]
    },
    {
        "section": "Identity - Awareness, measured, semi-automated",
        "questions": [
            "Have you implemented multi-factor authentication (MFA) for accessing sensitive systems and data?",
            "Is there a process in place to grant and revoke user access based on job roles and responsibilities?",
            "Do you regularly review and update user access permissions and privileges?",
            "Have you implemented strong password policies, including password complexity and expiration rules?"
        ]
    },
    {
        "section": "Identity - Committed, Continuous Improvement, Redundant",
        "questions": [
            "Is there a process for promptly deactivating accounts for employees who leave your organization?",
            "Do you use automated account provisioning and deprovisioning for user accounts?",
            "Have you implemented secure methods for user authentication and authorization?",
            "Does your organization enforce the principle of least privilege (users have the minimum access required to perform their duties)?"
        ]
    },
    {
        "section": "Identity - Service Aligned/Standardization/High Availability",
        "questions": [
            "Is there a process for reviewing and addressing accounts with excessive privileges?",
            "Do you maintain logs of user access and authorization activities?",
            "Is there a process for monitoring and detecting suspicious or unauthorized access attempts?",
            "Have you implemented encryption for sensitive data at rest and in transit?"
        ]
    },
    {
        "section": "Identity - Business Partnership/Innovation Optimized",
        "questions": [
            "Does your organization conduct security awareness training for employees?",
            "Have you established an incident response plan that includes identity and access management considerations?",
            "Is there a process for regular auditing and testing of identity and access controls?",
            "Does your organization regularly assess the effectiveness of your identity and access management program and make improvements as needed?"
        ]
    }
    # Add Protect, Detect, Respond, Recover, and CIS Controls sections here
]

# Display title
st.title("\U0001F9E0 IT Maturity Assessment Tool")
st.markdown("""
Welcome to the interactive IT Maturity Assessment. Please answer the following questions based on your current IT environment. Your responses will be used to calculate a maturity score across several technology domains.
""")

# Display form
with st.form("maturity_form"):
    responses = {}
    section_scores = {}
    for block in questionnaire:
        st.subheader(block["section"])
        yes_count = 0
        for q in block["questions"]:
            answer = st.radio(q, ["Yes", "No"], key=q)
            responses[q] = answer
            if answer == "Yes":
                yes_count += 1
        section_scores[block["section"]] = yes_count / len(block["questions"])
    submitted = st.form_submit_button("Submit")

if submitted:
    st.success("✅ Responses submitted successfully!")
    st.write("### Section Scores")
    st.write(section_scores)

    # Create and display bar chart
    df_scores = pd.DataFrame({"Section": list(section_scores.keys()), "Score": list(section_scores.values())})
    fig, ax = plt.subplots()
    ax.barh(df_scores["Section"], df_scores["Score"], color='skyblue')
    ax.set_xlabel("Maturity Score")
    ax.set_title("IT Maturity Score by Section")
    st.pyplot(fig)

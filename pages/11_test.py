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
    },
    {
        "section": "Protect - Survival, Ad-Hoc, Manual Legacy",
        "questions": [
            "Do you have a documented information security policy?",
            "Is there a process for classifying data and information assets based on sensitivity?",
            "Have you implemented access control measures to restrict unauthorized access to sensitive data?",
            "Do you regularly update and patch your software and systems to address known vulnerabilities?"
        ]
    },
    {
        "section": "Protect - Awareness, measured, semi-automated",
        "questions": [
            "Is there an established process for secure software development and code review?",
            "Have you implemented network segmentation to isolate critical systems and data from less secure areas?",
            "Is there an intrusion detection system (IDS) in place to monitor for suspicious network activities?",
            "Have you implemented firewalls to control inbound and outbound network traffic?"
        ]
    },
    {
        "section": "Protect - Committed, Continuous Improvement, Redundant",
        "questions": [
            "Is there a process for monitoring and responding to cybersecurity threats and incidents?",
            "Do you use encryption to protect sensitive data in transit and at rest?",
            "Have you implemented endpoint protection solutions (e.g., antivirus, anti-malware) on all devices?",
            "Is there a documented incident response plan that includes communication and coordination with stakeholders?"
        ]
    },
    {
        "section": "Protect - Service Aligned/Standardization/High Availability",
        "questions": [
            "Have you established secure configurations for your hardware and software?",
            "Do you conduct regular security awareness training for employees?",
            "Is there a process for managing and securing removable media (e.g., USB drives)?",
            "Have you implemented secure email and web browsing practices and technologies?"
        ]
    },
    {
        "section": "Protect - Business Partnership/Innovation Optimized",
        "questions": [
            "Is there a data backup and recovery plan in place, and are backups regularly tested?",
            "Do you have a secure mobile device management (MDM) solution for company-owned and BYOD devices?",
            "Is there a process for securely disposing of hardware and media containing sensitive data?",
            "Have you established secure supply chain practices to verify the security of third-party products and services?"
        ]
    },
    {
        "section": "Detect - Survival, Ad-Hoc, Manual Legacy",
        "questions": [
            "Do you have a dedicated team responsible for monitoring and detecting cybersecurity threats?",
            "Is there a process in place to continuously monitor network traffic for unusual or suspicious activities?",
            "Have you implemented intrusion detection systems (IDS) and intrusion prevention systems (IPS)?",
            "Is there a process for monitoring system and application logs for security events?"
        ]
    },
    {
        "section": "Detect - Awareness, measured, semi-automated",
        "questions": [
            "Do you regularly review and analyze security logs to detect potential threats?",
            "Is there a documented incident detection and reporting process in your organization?",
            "Have you implemented security information and event management (SIEM) solutions for centralized log and event analysis?",
            "Is there a process for threat intelligence collection and analysis to stay informed about emerging threats?"
        ]
    },
    {
        "section": "Detect - Committed, Continuous Improvement, Redundant",
        "questions": [
            "Do you use vulnerability scanning tools to identify weaknesses in your systems and applications?",
            "Have you implemented file integrity monitoring (FIM) to detect unauthorized changes to critical files?",
            "Is there a process for monitoring and detecting anomalies in user account activities and access?",
            "Do you use behavioral analytics to detect abnormal user behavior that may indicate a security threat?"
        ]
    },
    {
        "section": "Detect - Service Aligned/Standardization/High Availability",
        "questions": [
            "Is there a process for monitoring email traffic for phishing attempts and malicious attachments?",
            "Have you implemented endpoint detection and response (EDR) solutions on your devices?",
            "Is there a process for identifying and responding to unauthorized or rogue devices on your network?",
            "Do you use threat hunting techniques to proactively search for hidden threats within your network?"
        ]
    },
    {
        "section": "Detect - Business Partnership/Innovation Optimized",
        "questions": [
            "Is there a process for correlating and prioritizing security alerts based on risk?",
            "Do you conduct regular tabletop exercises to test your incident detection and response capabilities?",
            "Have you established key performance indicators (KPIs) to measure the effectiveness of your detection capabilities?",
            "Is there a documented process for communicating and coordinating incident detection and response with external stakeholders, such as law enforcement or industry groups?"
        ]
    }
]


# Display title
st.title("\U0001F9E0 Cybersecurity Maturity Assessment Tool")
st.markdown("""
Welcome to the interactive Cybersecurity Maturity Assessment. Please answer the following questions based on your current IT environment. Your responses will be used to calculate a maturity score across several technology domains.
""")

# Display title
st.title("\U0001F9E0 Cybersecurity Maturity Assessment Tool")
st.markdown("""
Welcome to the interactive Cybersecurity Maturity Assessment. Please answer the following questions based on your current IT environment. Your responses will be used to calculate a maturity score.
""")

# Display form
with st.form("maturity_form"):
    responses = {}
    section_scores = {}
    for block in questionnaire:
        st.subheader(block["section"])
        yes_count = 0
        for q in block["questions"]:
            answer = st.radio(q, ["Yes", "No"], key=f"{block['section']}_{q}")  # Unique keys
            responses[q] = answer
            if answer == "Yes":
                yes_count += 1
        if len(block["questions"]) > 0:
            section_scores[block["section"]] = yes_count / len(block["questions"])
    submitted = st.form_submit_button("Submit")

# Scoring and Results
if submitted:
    st.success("✅ Responses submitted successfully!")
    st.write("### Section Scores")
    if not section_scores:
        st.warning("No scores available.")
        st.stop()
    st.write(section_scores)

    # Bar Chart
    df_scores = pd.DataFrame({"Section": list(section_scores.keys()), "Score": list(section_scores.values())})
    df_scores = df_scores.sort_values(by="Score", ascending=True)
    fig, ax = plt.subplots()
    ax.barh(df_scores["Section"], df_scores["Score"], color='skyblue')
    ax.set_xlabel("Maturity Score")
    ax.set_title("IT Maturity Score by Section")
    st.pyplot(fig)

    # Radar Chart
    fig_radar, ax_radar = plt.subplots(figsize=(6, 6), subplot_kw={'projection': 'polar'})
    categories = list(section_scores.keys())
    values = list(section_scores.values())
    values += values[:1]  # Close the loop
    angles = [n / float(len(categories)) * 2 * 3.14159 for n in range(len(categories))]
    angles += angles[:1]

    ax_radar.plot(angles, values, linewidth=2, linestyle='solid')
    ax_radar.fill(angles, values, 'skyblue', alpha=0.4)
    ax_radar.set_yticklabels([])
    ax_radar.set_xticks(angles[:-1])
    ax_radar.set_xticklabels(categories, fontsize=8)
    ax_radar.set_title("Overall Cybersecurity Maturity Radar Chart", y=1.08)
    st.pyplot(fig_radar)

    # Interpretation Guide
    st.markdown("""
    ### 🔍 Interpretation:
    - **80%+**: High maturity — optimized or automated
    - **50-79%**: Moderate maturity — standardized or in transition
    - **Below 50%**: Low maturity — ad-hoc or siloed
    """)

    # Option to download scores as CSV
    st.download_button(
        label="📥 Download Section Scores",
        data=df_scores.to_csv(index=False),
        file_name="section_scores.csv",
        mime="text/csv"
    )


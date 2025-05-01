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
    },
    {
        "section": "Respond - Awareness, measured, semi-automated",
        "questions": [
            "Do you have predefined communication procedures for internal and external stakeholders during an incident?",
            "Have you identified and established contact information for key incident response contacts, both internal and external?",
            "Is there a documented procedure for preserving evidence and maintaining chain of custody during an incident?",
            "Do you regularly conduct tabletop exercises and simulations to test your incident response plan?"
        ]
    },
    {
        "section": "Respond - Committed, Continuous Improvement, Redundant",
        "questions": [
            "Is there a process for isolating and containing affected systems or networks during an incident?",
            "Have you established a procedure for collecting and analyzing forensic evidence to determine the scope and impact of an incident?",
            "Is there a process for documenting incident details, actions taken, and lessons learned?",
            "Have you identified and documented legal and regulatory reporting requirements in case of a data breach or incident?"
        ]
    },
    {
        "section": "Respond - Service Aligned/Standardization/High Availability",
        "questions": [
            "Is there a process for notifying affected individuals or organizations in compliance with data breach notification laws?",
            "Do you have predefined incident response playbooks for common incident types?",
            "Is there a process for coordinating incident response activities with external organizations, such as law enforcement or industry peers?",
            "Have you established a post-incident review process to assess the effectiveness of your response and identify areas for improvement?"
        ]
    },
    {
        "section": "Respond - Business Partnership/Innovation Optimized",
        "questions": [
            "Is there a documented process for providing executive management and relevant stakeholders with incident status updates?",
            "Do you maintain a record of past incidents and the actions taken to resolve them?",
            "Is there a process for conducting a root cause analysis of incidents to prevent future occurrences?",
            "Have you established key performance indicators (KPIs) and metrics to measure the effectiveness of your incident response capabilities?"
        ]
    },
    {
        "section": "Recover - Survival, Ad-Hoc, Manual Legacy",
        "questions": [
            "Do you have a documented business continuity and disaster recovery (BC/DR) plan in place?",
            "Is there a dedicated BC/DR team or a clearly defined BC/DR role within your organization?",
            "Have you identified critical business processes and assets that need to be prioritized for recovery?",
            "Is there a process for regularly backing up critical data and systems?"
        ]
    },
    {
        "section": "Recover - Awareness, measured, semi-automated",
        "questions": [
            "Have you established recovery time objectives (RTOs) and recovery point objectives (RPOs) for key systems and data?",
            "Is there a process for testing and validating backups to ensure they can be restored successfully?",
            "Do you have off-site or remote data backups to protect against physical disasters?",
            "Is there a documented procedure for restoring critical systems and data in a timely manner?"
        ]
    },
    {
        "section": "Recover - Committed, Continuous Improvement, Redundant",
        "questions": [
            "Have you identified and documented alternative IT infrastructure and facilities for use during recovery?",
            "Is there a process for notifying employees and stakeholders about recovery procedures and expectations?",
            "Do you conduct regular disaster recovery exercises to test your BC/DR plan?",
            "Is there a documented process for re-establishing network connectivity and access after an incident?"
        ]
    },
    {
        "section": "Recover - Service Aligned/Standardization/High Availability",
        "questions": [
            "Have you established a process for restoring user access and privileges in a secure manner?",
            "Is there a procedure for conducting a post-incident assessment to identify areas for recovery process improvement?",
            "Do you have a plan for ensuring that employees can work remotely if needed during a disruption?",
            "Is there a process for coordinating recovery efforts with third-party service providers and suppliers?"
        ]
    },
    {
        "section": "Recover - Business Partnership/Innovation Optimized",
        "questions": [
            "Have you identified and documented legal and regulatory reporting requirements related to recovery?",
            "Is there a process for communicating recovery progress and status updates to internal and external stakeholders?",
            "Do you maintain a record of past recovery efforts and lessons learned from incidents?",
            "Have you established key performance indicators (KPIs) and metrics to measure the effectiveness of your recovery capabilities?"
        ]
    },
    {
        "section": "CIS Controls - Survival, Ad-Hoc, Manual Legacy",
        "questions": [
            "Have you established and documented an inventory of authorized and unauthorized devices on your network?",
            "Is there a process in place to actively manage and control the use of administrative privileges?",
            "Do you regularly review and update software and systems to address known vulnerabilities?",
            "Have you implemented secure configurations for hardware and software used within your organization?"
        ]
    },
    {
        "section": "CIS Controls - Awareness, measured, semi-automated",
        "questions": [
            "Is there a process for continuous vulnerability assessment and remediation?",
            "Do you restrict and monitor the use of PowerShell, command-line tools, and other scripting languages?",
            "Have you implemented a process for the secure handling of account credentials, such as passwords and keys?",
            "Is there a documented process for data protection, including encryption, data classification, and data loss prevention?"
        ]
    },
    {
        "section": "CIS Controls - Committed, Continuous Improvement, Redundant",
        "questions": [
            "Do you actively monitor and analyze network traffic for signs of malicious activities?",
            "Have you established an incident response plan that includes roles, responsibilities, and communication procedures?",
            "Is there a process for logging and retaining security events and data for analysis?",
            "Do you regularly conduct security awareness training for employees and contractors?"
        ]
    },
    {
        "section": "CIS Controls - Service Aligned/Standardization/High Availability",
        "questions": [
            "Have you implemented secure email and web browsing practices and technologies?",
            "Is there a process for securely configuring and managing mobile devices used in your organization?",
            "Do you have a data backup and recovery plan that includes regular testing of backups?",
            "Is there a documented process for securely disposing of hardware and media containing sensitive data?"
        ]
    },
    {
        "section": "CIS Controls - Business Partnership/Innovation Optimized",
        "questions": [
            "Have you established a secure software development lifecycle (SDLC) process?",
            "Is there a process for securely configuring and monitoring cloud resources?",
            "Do you have a process for managing third-party security risks and ensuring secure supply chain practices?",
            "Is there a documented process for regular security assessments and audits?"
        ]
    }
]

# Display title
st.title("\U0001F9E0 Cybersecurity Maturity Assessment Tool")
st.markdown("""
Welcome to the interactive Cybersecurity Maturity Assessment. Please answer the following questions based on your current IT environment. Your responses will be used to calculate a maturity score across several technology domains.
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

# --- Maturity Scoring + Visualization ---
st.markdown("## 📊 Cybersecurity Maturity Summary")

# Aggregate scores
maturity_buckets = {
    "Survival": 0,
    "Awareness": 0,
    "Committed": 0,
    "Service": 0,
    "Business": 0
}
totals = {
    "Survival": 0,
    "Awareness": 0,
    "Committed": 0,
    "Service": 0,
    "Business": 0
}

# Count yes responses by category
for section in questionnaire:
    section_title = section["section"]
    category = None
    for key in maturity_buckets:
        if key in section_title:
            category = key
            break
    if category:
        totals[category] += len(section["questions"])
        for q in section["questions"]:
            if st.session_state.get(q) == "Yes":
                maturity_buckets[category] += 1

# Calculate percentages
percentages = {k: round((maturity_buckets[k] / totals[k]) * 100, 1) if totals[k] > 0 else 0 for k in maturity_buckets}

# Create DataFrame with conditional coloring
summary_df = pd.DataFrame({
    "Maturity Level": list(percentages.keys()),
    "Score (%)": list(percentages.values())
})

def color_score(val):
    if val >= 75:
        color = 'lightgreen'
    elif val >= 50:
        color = 'khaki'
    else:
        color = 'salmon'
    return f'background-color: {color}'

st.dataframe(summary_df.style.applymap(color_score, subset=["Score (%)"]))

# Display bar chart
fig, ax = plt.subplots()
colors = [
    'green' if val >= 75 else 'orange' if val >= 50 else 'red'
    for val in summary_df["Score (%)"]
]
ax.bar(summary_df["Maturity Level"], summary_df["Score (%)"], color=colors)
ax.set_ylabel("Maturity Score (%)")
ax.set_ylim([0, 100])
ax.set_title("Cybersecurity Maturity by Capability Level")
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


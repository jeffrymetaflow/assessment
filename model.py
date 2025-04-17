import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

# Sidebar Navigation
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", [
    "🧠 Overview Summary",
    "⚙️ Inputs Setup",
    "📊 ITRM Calculator",
    "💰 ITRM Financial Summary",
    "🔐 Cybersecurity Assessment",
    "📝 IT Maturity Assessment",
    "🧭 Strategic Roadmap",
    "📊 Benchmarking & Persona",
    "🤖 AI Assistant"
])
client_name = st.sidebar.text_input("Client Name", placeholder="e.g., Acme Corp")

if "baseline_revenue" not in st.session_state:
    st.session_state.baseline_revenue = 0  # Replace 0 with a meaningful default value

if "category_expenses_to_total" not in st.session_state:
    st.session_state.category_expenses_to_total = [0.1] * 5  # Default: 5 categories with 10% each

if "category_revenue_to_total" not in st.session_state:
    st.session_state.category_revenue_to_total = [0.05] * 5  # Default: 5 categories with 5% each

if "revenue_growth" not in st.session_state:
    st.session_state.revenue_growth = [0.05] * 3  # Default growth rate: 5% per year for 3 years

if "expense_growth" not in st.session_state:
    st.session_state.expense_growth = [0.03] * 3  # Default growth rate: 3% per year for 3 years

# Strategic Roadmap Tab
if section == "🧭 Strategic Roadmap":
    st.title("🧭 Strategic Roadmap")
    st.markdown("""
    Based on your assessment scores and ITRM trajectory, this roadmap offers recommended actions.
    """)

    roadmap_items = []
    checklist = []

    if 'it_maturity_scores' in st.session_state:
        scores = st.session_state.it_maturity_scores
        for _, row in scores.iterrows():
            score = row["Score (%)"]
            cat = row["Category"]
            if score >= 80:
                label = "🟢 Maintain and enhance automation"
                rec = f"🟢 {cat}: Maintain and enhance automation."
            elif score >= 50:
                label = "🟡 Standardize and document processes"
                rec = f"🟡 {cat}: Standardize and document processes."
            else:
                label = "🔴 Prioritize investment and leadership support"
                rec = f"🔴 {cat}: Prioritize investment and leadership support."
            roadmap_items.append((cat, label))
            checklist.append(rec)

    if 'cybersecurity_scores' in st.session_state:
        for control, score in st.session_state.cybersecurity_scores.items():
            if score >= 4:
                label = "✅ Sustain mature practices"
                rec = f"✅ {control}: Sustain mature practices."
            elif score == 3:
                label = "⚠️ Refine documentation and training"
                rec = f"⚠️ {control}: Consider refining documentation and training."
            else:
                label = "❌ Prioritize process implementation and governance"
                rec = f"❌ {control}: Prioritize process implementation and governance."
            roadmap_items.append((control, label))
            checklist.append(rec)

    # Ensure both arrays have the same length
    quarters = ["Q1", "Q2", "Q3", "Q4"] * ((len(roadmap_items) + 3) // 4)
    quarters = quarters[:len(roadmap_items)]  # Trim to match the length of roadmap_items

    # Create DataFrame with proper alignment
    timeline_df = pd.DataFrame({
        "Quarter": quarters,
        "Action Item": roadmap_items  # Ensure matching lengths
    })

    if roadmap_items:
        st.subheader("📅 Strategic Timeline by Quarter")
        timeline_df = timeline_df.dropna().reset_index(drop=True)
        st.dataframe(timeline_df)

        st.subheader("✅ Progress Tracker")
        for quarter in ["Q1", "Q2", "Q3", "Q4"]:
            st.markdown(f"**{quarter}**")
            for item in timeline_df[timeline_df["Quarter"] == quarter]["Action Item"]:
                st.checkbox(f"{item[0]} – {item[1]}", key=f"{quarter}_{item[0]}" )

    if checklist:
        st.markdown("---")
        st.subheader("🗒️ Your Strategic Checklist")
        for item in checklist:
            st.markdown(f"- [ ] {item}")

# Benchmarking & Persona Tab
elif section == "📊 Benchmarking & Persona":
    st.title("📊 Benchmarking & Persona")

    industry = st.selectbox("Select Industry", ["Healthcare", "Financial Services", "Retail", "Manufacturing", "Education", "Other"])
    company_size = st.selectbox("Select Company Size", ["< 500 employees", "500–5000", "> 5000"])
    user_role = st.radio("Your Role", ["CIO", "IT Director", "IT Ops", "Finance", "Other"])

    st.session_state.client_profile = {
        "industry": industry,
        "company_size": company_size,
        "user_role": user_role
    }

    st.subheader("📈 Industry Benchmarks")
    benchmark_data = {
        "Healthcare": [80, 65, 60, 50, 35],
        "Financial Services": [85, 75, 70, 55, 40],
        "Retail": [70, 60, 55, 45, 30],
        "Manufacturing": [75, 68, 62, 50, 38],
        "Education": [65, 55, 50, 40, 25],
        "Other": [72, 60, 57, 46, 32]
    }
    benchmark_df = pd.DataFrame({
        "Category": ["Managed / Automated", "Standardized / Optimized", "Defined / Measured", "Reactive / Operational", "Survival, Ad-Hoc, Manual Legacy"],
        "Industry Average (%)": benchmark_data[industry]
    })
    st.dataframe(benchmark_df)

    if 'it_maturity_scores' in st.session_state:
        user_df = st.session_state.it_maturity_scores
        compare_df = pd.merge(user_df, benchmark_df, on="Category")
        compare_df["Gap"] = compare_df["Score (%)"] - compare_df["Industry Average (%)"]
        st.subheader("📊 Your Score vs Industry Average")
        st.dataframe(compare_df)
        st.bar_chart(compare_df.set_index("Category")[["Score (%)", "Industry Average (%)"]])
    else:
        st.info("Complete the IT Maturity Assessment to see benchmark comparisons.")
elif section == "📊 Benchmarking & Persona":
    st.title("📊 Benchmarking & Persona")

    industry = st.selectbox("Select Industry", ["Healthcare", "Financial Services", "Retail", "Manufacturing", "Education", "Other"])
    company_size = st.selectbox("Select Company Size", ["< 500 employees", "500–5000", "> 5000"])
    user_role = st.radio("Your Role", ["CIO", "IT Director", "IT Ops", "Finance", "Other"])

    st.session_state.client_profile = {
        "industry": industry,
        "company_size": company_size,
        "user_role": user_role
    }

    st.subheader("📈 Benchmarked Averages (Mock Data)")
    bench_df = pd.DataFrame({
        "Category": ["Managed / Automated", "Standardized / Optimized", "Defined / Measured", "Reactive / Operational", "Survival, Ad-Hoc, Manual Legacy"],
        "Industry Average (%)": [82, 68, 63, 47, 30]
    })
    st.dataframe(bench_df)

    if 'it_maturity_scores' in st.session_state:
        user_df = st.session_state.it_maturity_scores
        compare_df = pd.merge(user_df, bench_df, on="Category")
        compare_df["Gap"] = compare_df["Score (%)"] - compare_df["Industry Average (%)"]
        st.subheader("📊 Your Score vs Industry Average")
        st.dataframe(compare_df)
        st.bar_chart(compare_df.set_index("Category")[["Score (%)", "Industry Average (%)"]])
    else:
        st.info("Complete the IT Maturity Assessment to see benchmark comparisons.")

# Overview Tab
if section == "🧠 Overview Summary":
    st.title("🧠 IT Revenue Margin Strategy Summary")
    itrm_summary = """
**Title:** IT Revenue Margin (ITRM) Overview Summary  
**Subtitle:** Optimizing IT Efficiency with AI-Driven Solutions  
**Prepared by:** IT Strategy and Innovation Team

---

## Overview
This IT strategy session introduces an AI-driven IT optimization framework to help <Client Name> define a technology roadmap that reduces IT Revenue Margin, enhances IT resilience, and aligns IT investments with revenue growth. This approach provides end-to-end infrastructure, security, and data management strategies that support a dynamic, cost-effective IT environment.

---

## IT Strategy
Real-time IT ecosystem monitoring and automation ensures <Client Name>'s IT efficiency scales with business demand.

- Performance monitoring tools proactively optimize IT performance, reducing unnecessary resource consumption.  
- Security and compliance solutions help prevent risks that could impact IT revenue margins.  
- Systems management platforms automate IT workflows, reducing manual effort and operational costs.  

---

## IT Revenue Margin Calculation
By leveraging AI-driven infrastructure optimization tools, <Client Name> can dynamically adjust IT resource consumption.

- Monitoring and automation tools drive automated cost reduction in IT infrastructure.  
- Intelligent storage optimization reduces infrastructure costs significantly, directly improving IT Revenue Margin.  
- Comprehensive backup and recovery solutions ensure business continuity by minimizing downtime and disaster recovery costs.  

---

## ITRM Recommendations and Implementation
### Optimized IT Ecosystem Strategy

- Hybrid Cloud Optimization: Tools that dynamically shift workloads can reduce IT costs while maintaining high uptime.  
- Security and Compliance Enhancements: Solutions that mitigate risks and ensure regulatory compliance reduce overhead and increase system integrity.  
- IT Workflow Automation: Automation platforms streamline IT operations, enhancing productivity and efficiency.  

---

## Next Steps
1. Conduct ITRM Workshops – Offer CIOs and CTOs a structured assessment of their IT Revenue Margin and cost efficiency.  
2. Develop a Modular ITRM Dashboard – Create a scalable, subscription-based IT efficiency monitoring platform.  
3. Bundle IT Optimization Tools – Promote integration of performance monitoring, backup, automation, and security into a unified solution.  
4. Establish CIO Advisory Services – Use the ITRM deliverable as a lead-generation and strategic advisory tool.  

By adopting an AI-optimized IT revenue framework, <Client Name> can align IT operations with business performance, reduce waste, and ensure technology investments deliver maximum ROI.

**IT Revenue Margin – Driving Efficiency for Digital Transformation.**
"""

    summary_display = itrm_summary.replace("<Client Name>", client_name) if client_name else itrm_summary
    st.markdown(summary_display, unsafe_allow_html=True)

    if st.button("📄 Download Executive Summary PDF"):
        class PDF(FPDF):
            def header(self):
                self.set_font("Arial", "B", 12)
                self.cell(0, 10, "IT Revenue Margin Executive Summary", ln=True, align="C")
                self.ln(5)

            def chapter_title(self, title):
                self.set_font("Arial", "B", 12)
                self.cell(0, 10, title, ln=True, align="L")

            def chapter_body(self, body):
                self.set_font("Arial", "", 11)
                self.multi_cell(0, 10, body)

        pdf = PDF() # Ensure this is after the class definition
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.chapter_title("Client: " + (client_name if client_name else "<Client Name>"))
        cleaned_summary = summary_display.replace("**", "").replace("<Client Name>", client_name if client_name else "<Client Name>").replace("  ", "").replace("## ", "").replace("### ", "").replace("---", "----------------------")
        cleaned_summary = cleaned_summary.encode("latin-1", "ignore").decode("latin-1")
        pdf.chapter_body(cleaned_summary)

        # Add ITRM trend chart if available
        if 'calculator_results' in st.session_state:
            results = st.session_state.calculator_results
            years = list(results.keys())
            itrms = [results[y]['ITRM'] for y in years]

            fig, ax = plt.subplots()
            ax.plot(years, itrms, marker='o', linewidth=2)
            ax.set_ylabel("IT Revenue Margin (%)")
            ax.set_title("ITRM Over Time")

            chart_buffer = BytesIO()
            fig.savefig(chart_buffer, format="PNG")
            chart_buffer.seek(0)

            pdf.add_page()
            pdf.chapter_title("ITRM Trend Chart")
            pdf.image(chart_buffer, x=10, y=None, w=180)

        buffer = BytesIO()
        pdf.output(buffer)

        # Add IT Maturity Scores
        if 'it_maturity_scores' in st.session_state:
            maturity_df = st.session_state.it_maturity_scores
            pdf.add_page()
            pdf.chapter_title("IT Maturity Assessment Summary")
            for index, row in maturity_df.iterrows():
                line = f"{row['Category']}: {row['Score (%)']}%"
                pdf.chapter_body(line)

        # Add Financial Summary Insights
        if 'calculator_results' in st.session_state:
            results = st.session_state.calculator_results
            last_year = 'Year 3'
            pdf.add_page()
            pdf.chapter_title("Financial Summary Insights")
            if 'inputs' in st.session_state:
                inputs = st.session_state.inputs
                categories = ["Category 1", "Category 2", "Category 3", "Category 4", "Category 5"]
                revenue = inputs['revenue_baseline'] * (1 + inputs['target_revenue_growth'][2])
                for i, cat in enumerate(categories):
                    split = inputs['category_revenue_split'][i]
                    expense = results[last_year]['category_expenses'][i]
                    pdf.chapter_body(f"{cat}: ${expense:,.2f} expense, {split * 100:.1f}% of revenue")
        buffer.seek(0)
        st.download_button("📥 Download PDF", buffer, file_name="ITRM_Executive_Summary.pdf")
   
# Financial Summary Tab
if section == "💰 ITRM Financial Summary":
    st.title("💰 ITRM Financial Summary")
    
    # Get baseline revenue and expense from session state or inputs
    if 'baseline_revenue' not in st.session_state or 'it_expense' not in st.session_state:
        st.warning("Please configure inputs in the 'Inputs Setup' tab first.")
        st.stop()

    # Retrieve session state data
    baseline_revenue = st.session_state.baseline_revenue
    it_expense = st.session_state.it_expense
    category_expenses_to_total = st.session_state.category_expenses_to_total
    category_revenue_to_total = st.session_state.category_revenue_to_total
    revenue_growth = st.session_state.revenue_growth
    expense_growth = st.session_state.expense_growth

    # Allow user to adjust growth rates for each year (Year 1, Year 2, Year 3)
    st.markdown("### Adjust Revenue Growth and Expense Growth")
    new_revenue_growth = [st.slider(f"Year {i+1} Revenue Growth (%)", 0.0, 100.0, value=float(revenue_growth[i] * 100)) for i in range(3)]
    new_expense_growth = [st.slider(f"Year {i+1} Expense Growth (%)", 0.0, 100.0, value=float(expense_growth[i] * 100)) for i in range(3)]

    # Calculate the updated revenue and expenses
    revenue_input = {
        "Year 1": baseline_revenue * (1 + new_revenue_growth[0] / 100),  # Adjust baseline by growth rate
        "Year 2": baseline_revenue * (1 + new_revenue_growth[1] / 100),
        "Year 3": baseline_revenue * (1 + new_revenue_growth[2] / 100),
    }

    expense_input = {
        "Year 1": it_expense * (1 + new_expense_growth[0] / 100),  # Adjust baseline by expense growth rate
        "Year 2": it_expense * (1 + new_expense_growth[1] / 100),
        "Year 3": it_expense * (1 + new_expense_growth[2] / 100),
    }

    # Show updated revenue and expenses
    st.markdown("### Updated Revenue:")
    for year, revenue in revenue_input.items():
        st.markdown(f"- **{year}:** ${revenue:,.2f}")

    st.markdown("### Updated Expenses:")
    for year, expense in expense_input.items():
        st.markdown(f"- **{year}:** ${expense:,.2f}")

    # Calculate IT Revenue Margin (ITRM) for each year
     itrm = {
        "Year 1": (expense_input["Year 1"] / revenue_input["Year 1"]) * 100 if revenue_input["Year 1"] != 0 else 0,
        "Year 2": (expense_input["Year 2"] / revenue_input["Year 2"]) * 100 if revenue_input["Year 2"] != 0 else 0,
        "Year 3": (expense_input["Year 3"] / revenue_input["Year 3"]) * 100 if revenue_input["Year 3"] != 0 else 0,
     }

    # Display ITRM
    st.markdown(f"### IT Revenue Margin (ITRM) for Year 1: {itrm['Year 1']:.2f}%")
    st.markdown(f"### IT Revenue Margin (ITRM) for Year 2: {itrm['Year 2']:.2f}%")
    st.markdown(f"### IT Revenue Margin (ITRM) for Year 3: {itrm['Year 3']:.2f}%")

    # Plot ITRM Trend
    st.markdown("### 📈 ITRM Trend Over Time")
    years = ["Year 1", "Year 2", "Year 3"]
    itrms = [itrm["Year 1"], itrm["Year 2"], itrm["Year 3"]]

    fig, ax = plt.subplots()
    ax.plot(years, itrms, marker='o', linewidth=2)
    ax.set_ylabel("IT Revenue Margin (%)")
    ax.set_title("ITRM Over Time")
    st.pyplot(fig)

    # Recommendations Based on ITRM
    st.markdown("### Dynamic Recommendations")
    for year in ["Year 1", "Year 2", "Year 3"]:
        if itrm[year] < 20:
            st.markdown(f"🔴 **{year}**: Consider cutting costs in the highest expense categories or increasing investment in automation.")
        elif itrm[year] < 40:
            st.markdown(f"🟡 **{year}**: Standardize processes and improve IT cost management strategies.")
        else:
            st.markdown(f"🟢 **{year}**: Maintain and enhance automation to ensure continued growth and efficiency.")
            
# Cybersecurity Assessment Tab
elif section == "🔐 Cybersecurity Assessment":
    st.title("🔐 Cybersecurity Maturity Assessment")
    st.markdown("For more details, visit the [NIST Cybersecurity Framework website](https://www.nist.gov/).")

    st.markdown("""
    **NIST Cybersecurity Framework Functions:**

    - **Identify:** Understand the business context, the resources that support critical functions, and the related cybersecurity risks.
    - **Protect:** Develop and implement safeguards to ensure the delivery of critical services.
    - **Detect:** Identify the occurrence of a cybersecurity event in a timely manner.
    - **Respond:** Take action regarding a detected cybersecurity incident.
    - **Recover:** Maintain plans for resilience and restore capabilities or services impaired due to a cybersecurity incident.
    """)

    nist_controls = [
        "Identify - Asset Management",
        "Protect - Access Control",
        "Protect - Data Security",
        "Detect - Anomalies and Events",
        "Respond - Response Planning",
        "Recover - Recovery Planning"
    ]

    st.markdown("""
Please rate your cybersecurity maturity against the **NIST Cybersecurity Framework** categories. Use the scale below to self-assess how well your organization addresses each area:

- **1 – Not Started**: No formal practices or policies in place.
- **2 – Initial**: Informal practices exist but are not documented or consistent.
- **3 – Developing**: Documented practices exist, but only partially implemented.
- **4 – Managed**: Practices are implemented and actively managed.
- **5 – Optimized**: Practices are well-integrated and continuously improved.
""")

    responses = []
    for control in nist_controls:
        score = st.slider(control, min_value=1, max_value=5, value=3, key=f"cyber_nist_{control}")
        responses.append(score)

    st.session_state.cybersecurity_scores = dict(zip(nist_controls, responses))
    average_score = sum(responses) / len(responses)

    # Maturity Heatmap
    st.subheader("🧭 Maturity Heatmap")
    fig, ax = plt.subplots(figsize=(8, 1))
    ax.imshow([responses], cmap='YlGn', aspect='auto')
    ax.set_xticks(range(len(nist_controls)))
    ax.set_xticklabels(nist_controls, rotation=45, ha="right")
    ax.set_yticks([])
    ax.set_title("NIST Domain Maturity Levels")
    for i, score in enumerate(responses):
        ax.text(i, 0, str(score), va='center', ha='center', color='black')
    st.pyplot(fig)

    st.markdown(f"### 🧮 Overall Cybersecurity Maturity Score: **{average_score:.2f} / 5**")
    st.markdown(f"### 🧮 Overall Cybersecurity Maturity Score: **{average_score:.2f} / 5**")

    if average_score >= 4.5:
        st.success("Excellent maturity. Your cybersecurity posture appears robust.")
    elif average_score >= 3.0:
        st.info("Moderate maturity. Consider targeted improvements in specific areas.")
    else:
        st.warning("Low maturity. Immediate enhancements are recommended to reduce risk.")

    st.subheader("🧩 Automated NIST Category Recommendations")
    recommendations = {
        "Identify - Asset Management": "Ensure a complete and regularly updated inventory of all hardware, software, and data assets.",
        "Protect - Access Control": "Implement strong identity and access management (IAM) protocols with role-based access.",
        "Protect - Data Security": "Apply encryption, secure data storage, and data classification policies.",
        "Detect - Anomalies and Events": "Deploy SIEM tools and configure alerts for anomalous behavior.",
        "Respond - Response Planning": "Establish and routinely test an incident response plan.",
        "Recover - Recovery Planning": "Maintain and validate data backups and recovery procedures." 
    }

    for control, score in zip(nist_controls, responses):
        if score <= 3:
            st.warning(f"🔍 {control}: {recommendations[control]}")
        else:
            st.success(f"✅ {control}: Maturity level is sufficient.")
        st.warning("Low maturity. Immediate enhancements are recommended to reduce risk.")

# AI Assistant Tab
elif section == "🤖 AI Assistant":
    from openai import OpenAI, OpenAIError, RateLimitError, AuthenticationError
    from streamlit_chat import message

    st.title("🤖 AI Assistant")

    if "OPENAI_API_KEY" not in st.secrets:
        st.warning("🤖 AI Assistant is temporarily unavailable. Please add your OpenAI API key in Streamlit Secrets.")
    else:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "system", "content": "You are an expert IT strategy assistant helping explain IT Revenue Margin modeling to business leaders."}
            ]

        user_input = st.text_input("Ask the assistant anything about your IT model or strategy:")

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.spinner("Thinking..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=st.session_state.messages
                    )
                    msg = response.choices[0].message.content
                    st.session_state.messages.append({"role": "assistant", "content": msg})
                except RateLimitError:
                    st.error("🚦 OpenAI rate limit exceeded. Please try again later or check your billing settings.")
                except AuthenticationError:
                    st.error("🔐 Authentication failed. Please verify your API key and billing setup.")
                except OpenAIError as e:
                    st.error(f"💥 OpenAI Error: {str(e)}")

        for i, msg in enumerate(st.session_state.messages[1:]):
            is_user = (i % 2 == 0)
            message(msg["content"], is_user=is_user)


elif section == "📝 IT Maturity Assessment":
    st.title("📝 IT Maturity Assessment Tool")
    st.markdown("""
    Welcome to the interactive IT Maturity Assessment. Please answer the following questions 
    based on your current IT environment. Your responses will be used to calculate a maturity score
    across several technology domains.
    """)

    grouped_questions = {
    "Managed / Automated": [
        "Failover between sites",
        "Software Intelligence",
        "Automated patch management",
        "Self-healing infrastructure",
        "Integrated asset and configuration management",
        "AI-driven capacity forecasting"
    ],
    "Standardized / Optimized": [
        "Documented configuration baselines",
        "Centralized logging and monitoring",
        "Defined performance SLAs",
        "Integrated IT service management",
        "Scheduled DR testing",
        "Standardized vendor management process"
    ],
    "Defined / Measured": [
        "Service catalog in place",
        "Change management policy",
        "IT financial transparency dashboards",
        "Defined KPIs and scorecards",
        "Maturity model assessments scheduled",
        "Performance benchmarks in place"
    ],
    "Reactive / Operational": [
        "Ticket-based support system",
        "Manual security patching",
        "Email-based approval workflows",
        "Unstructured vendor reporting",
        "Ad-hoc root cause analysis",
        "Basic uptime monitoring"
    ],
    "Survival, Ad-Hoc, Manual Legacy": [
        "Back Up for restoring in case of data center disaster",
        "No defined IT process for onboarding",
        "Spreadsheets used for asset tracking",
        "No disaster recovery plan",
        "Unstructured documentation",
        "Undefined service ownership"
    ]
}

    responses = {}

    with st.form("maturity_form"):
        for category, questions in grouped_questions.items():
            st.subheader(category.strip())
            for q in questions:
                key = f"{category.strip()}::{q}"
                responses[key] = st.radio(q.strip(), ["Yes", "No"], key=key)
        submitted = st.form_submit_button("Submit Assessment")

    if submitted:
        st.header("📊 Maturity Assessment Results")
        score_data = []

        for category in grouped_questions:
            questions = grouped_questions[category]
            yes_count = sum(1 for q in questions if responses.get(f"{category.strip()}::{q}") == "Yes")
            total = len(questions)
            percent = round((yes_count / total) * 100, 1)
            score_data.append({"Category": category.strip(), "Score (%)": percent})

        score_df = pd.DataFrame(score_data).sort_values(by="Category")
        st.session_state.it_maturity_scores = score_df

        st.dataframe(score_df, use_container_width=True)

        st.subheader("🔵 Heatmap View of Maturity by Category")
        st.dataframe(score_df.style.format({"Score (%)": "{:.1f}"}))

        st.subheader("📈 Bar Chart of Scores")
        st.bar_chart(score_df.set_index("Category"))

        st.markdown("""
        ### 🔍 Interpretation:
        - **80%+**: High maturity — optimized or automated
        - **50-79%**: Moderate maturity — standardized or in transition
        - **Below 50%**: Low maturity — ad-hoc or siloed
        """)

        st.header("🧭 Recommendations by Category")
        for _, row in score_df.iterrows():
            score = row["Score (%)"]
            category = row["Category"]
            if score >= 80:
                rec = f"✅ *{category}* is highly mature. Continue optimizing with automation and cross-domain integration."
            elif score >= 50:
                rec = f"⚠️ *{category}* shows moderate maturity. Focus on standardization, consolidation, and governance improvements."
            else:
                rec = f"❌ *{category}* is low maturity. Prioritize modernization, documentation, and automation."
            st.markdown(rec)

            # Function to generate AI-powered cybersecurity recommendations based on maturity scores
            def generate_cybersecurity_recommendations(cybersecurity_scores):
                recommendations = []
                for category, score in cybersecurity_scores.items():
                    if category == "Identify":
                        if score >= 4:
                            recommendation = "✅ **Identify**: Sustain mature practices, monitor emerging trends, and ensure your cybersecurity risk management processes are consistently updated."
                        elif score == 3:
                            recommendation = "⚠️ **Identify**: Review and improve risk management processes, including threat detection, vulnerability assessments, and mitigation planning."
                        else:
                            recommendation = "❌ **Identify**: Establish robust risk management practices, conduct regular vulnerability assessments, and develop proactive threat detection mechanisms."
                    
                    elif category == "Protect":
                        if score >= 4:
                            recommendation = "✅ **Protect**: Maintain strong preventive controls, continue training, and enhance system defense capabilities."
                        elif score == 3:
                            recommendation = "⚠️ **Protect**: Enhance preventive controls and conduct regular system security assessments."
                        else:
                            recommendation = "❌ **Protect**: Focus on improving access controls, patch management, and data encryption strategies."
                    
                    elif category == "Detect":
                        if score >= 4:
                            recommendation = "✅ **Detect**: Sustain continuous monitoring and analysis of cybersecurity events to detect anomalies promptly."
                        elif score == 3:
                            recommendation = "⚠️ **Detect**: Strengthen real-time detection systems and incident response protocols."
                        else:
                            recommendation = "❌ **Detect**: Implement and fine-tune anomaly detection tools and integrate proactive monitoring systems."
                    
                    elif category == "Respond":
                        if score >= 4:
                            recommendation = "✅ **Respond**: Ensure ongoing incident response planning and regular testing to handle potential threats effectively."
                        elif score == 3:
                            recommendation = "⚠️ **Respond**: Create and regularly test an incident response plan and conduct training for key stakeholders."
                        else:
                            recommendation = "❌ **Respond**: Develop and implement an incident response plan, ensuring clear roles, responsibilities, and procedures during cybersecurity incidents."
                    
                    elif category == "Recover":
                        if score >= 4:
                            recommendation = "✅ **Recover**: Continue to strengthen recovery processes and maintain regular testing of disaster recovery plans."
                        elif score == 3:
                            recommendation = "⚠️ **Recover**: Review recovery processes and update your disaster recovery plan."
                        else:
                            recommendation = "❌ **Recover**: Focus on developing and testing disaster recovery plans to minimize downtime during cybersecurity breaches."
                    
                    recommendations.append(recommendation)
                return recommendations
            
            # AI Assistant function to provide personalized responses based on cybersecurity scores
            def ai_assistant(query):
                if 'cybersecurity_scores' in st.session_state:
                    recommendations = generate_cybersecurity_recommendations(st.session_state.cybersecurity_scores)
                    return "\n".join(recommendations)
                else:
                    return "I can assist you with IT maturity and recommendations based on your inputs."
            
            # Display the AI Assistant interaction in the app
            st.sidebar.title("AI Assistant")
            query = st.text_input("Ask the AI Assistant:", placeholder="e.g., What are the cybersecurity recommendations?")
            
            if query:
                response = ai_assistant(query)
                st.markdown(f"**AI Assistant Response:**\n{response}")
            
            # Sidebar navigation for the app
            section = st.sidebar.radio("Go to", ["🧠 Overview Summary", "📊 ITRM Calculator", "💰 ITRM Financial Summary", "🔐 Cybersecurity Assessment", "📝 IT Maturity Assessment", "🧭 Strategic Roadmap", "📊 Benchmarking & Persona", "🤖 AI Assistant"])
            
            # AI Assistant Tab Content
            if section == "🤖 AI Assistant":
                st.title("AI Assistant")
                st.markdown("Ask the assistant anything about your IT model or strategy.")
                st.text_area("Your Question", value="", height=100)

    # AI Assistant Function to update values in the session state
    def ai_assistant_update(query):
        response = ""
    
        # Update baseline revenue
        if "baseline revenue" in query.lower():
            try:
                new_revenue = float(query.split("update baseline revenue to ")[1].replace(",", ""))
                st.session_state.baseline_revenue = new_revenue
                response = f"✅ Baseline revenue has been updated to ${new_revenue:,.2f}."
            except ValueError:
                response = "❌ Couldn't parse the revenue amount. Please ensure it's a valid number."
    
        # Update IT expenses
        elif "it expense" in query.lower():
            try:
                new_expense = float(query.split("update IT expense to ")[1].replace(",", ""))
                st.session_state.it_expense = new_expense
                response = f"✅ IT Expense has been updated to ${new_expense:,.2f}."
            except ValueError:
                response = "❌ Couldn't parse the expense amount. Please ensure it's a valid number."
    
        # Handle other inputs (categories, revenue growth, etc.) similarly...
        return response
    
    # AI Assistant Tab - User Interface
    if section == "🤖 AI Assistant":
        st.title("AI Assistant")
    
        user_input = st.text_input("Ask the AI Assistant to update the Inputs:")
    
        if user_input:
            assistant_response = ai_assistant_update(user_input)
            st.markdown(assistant_response)
    
            # Display the updated values
            st.write(f"Current Baseline Revenue: ${st.session_state.baseline_revenue:,.2f}")
            st.write(f"Current IT Expense: ${st.session_state.it_expense:,.2f}")
    
        # You can add more examples or guidelines here
        st.markdown("You can update values such as baseline revenue, IT expense, and more.")
        st.write("Example commands: \n- 'Update baseline revenue to 1,000,000' \n- 'Update IT expense to 500,000'")
    
    # Inputs Tab - To reflect updates made by the AI Assistant
    if section == "⚙️ Inputs Setup":
        st.title("Inputs Setup")
        st.markdown("Configure your baseline inputs and growth expectations.")
    
        revenue = st.session_state.get("baseline_revenue", 0.0)
        it_expense = st.session_state.get("it_expense", 0.0)
    
        # Dynamically update input fields
        revenue_input = st.number_input("Baseline Revenue ($)", value=revenue, step=1000000)
        expense_input = st.number_input("IT Expense ($)", value=it_expense, step=100000)
    
        if revenue_input != revenue:
            st.session_state.baseline_revenue = revenue_input
        if expense_input != it_expense:
            st.session_state.it_expense = expense_input

# Inputs Tab
if section == "⚙️ Inputs Setup":
    st.title("⚙️ Inputs Setup")

    # Input Fields for Baseline Revenue, IT Expenses, and Growth Rates
    baseline_revenue = st.number_input("Baseline Revenue ($)", value=739_000_000)
    it_expense = st.number_input("IT Expense Baseline ($)", value=4_977_370)

    # Expense and Revenue Percentages
    category_expenses_to_total = [
        st.number_input(f"Category {i+1} % of IT Expenses", value=0.1) for i in range(5)
    ]
    
    category_revenue_to_total = [
        st.number_input(f"Category {i+1} % of Revenue", value=0.05) for i in range(5)
    ]

    # Growth Rates
    revenue_growth = [
        st.number_input(f"Year {i+1} Revenue Growth (%)", value=0.05) for i in range(3)
    ]
    expense_growth = [
        st.number_input(f"Year {i+1} Expense Growth (%)", value=0.03) for i in range(3)
    ]

    # Save inputs to session_state
    if st.button("Save Inputs"):
        st.session_state.baseline_revenue = baseline_revenue
        st.session_state.it_expense = it_expense
        st.session_state.category_expenses_to_total = category_expenses_to_total
        st.session_state.category_revenue_to_total = category_revenue_to_total
        st.session_state.revenue_growth = revenue_growth
        st.session_state.expense_growth = expense_growth
        st.success("Inputs saved successfully!")

    # Show the inputs in a clean table
    input_data = {
        "Parameter": [
            "Baseline Revenue ($)", "IT Expense Baseline ($)", 
            "Category 1 % of IT Expenses", "Category 2 % of IT Expenses", 
            "Category 3 % of IT Expenses", "Category 4 % of IT Expenses", 
            "Category 5 % of IT Expenses", "Category 1 % of Revenue", 
            "Category 2 % of Revenue", "Category 3 % of Revenue", 
            "Category 4 % of Revenue", "Category 5 % of Revenue",
            "Year 1 Revenue Growth (%)", "Year 2 Revenue Growth (%)", 
            "Year 3 Revenue Growth (%)", "Year 1 Expense Growth (%)", 
            "Year 2 Expense Growth (%)", "Year 3 Expense Growth (%)"
        ],
        "Value": [
            baseline_revenue, it_expense,
            *category_expenses_to_total,
            *category_revenue_to_total,
            *revenue_growth,
            *expense_growth
        ]
    }

    inputs_df = pd.DataFrame(input_data)

    st.subheader("Review Inputs")
    st.dataframe(inputs_df)

    # Clear any unnecessary session data
    st.session_state.pop('inputs', None)  # Remove the 'inputs' key to avoid potential display issues

    if section == "⚙️ Inputs Setup":
        st.title("Inputs Setup")
        st.markdown("Configure your baseline inputs and growth expectations.")
    
        revenue = st.session_state.get("baseline_revenue", 0.0)
        it_expense = st.session_state.get("it_expense", 0.0)
    
    # Ensure revenue is a valid numeric value
    baseline_revenue = st.session_state.get("baseline_revenue", 739000000)
    
    # If it's a string (e.g., '1,000,000'), clean it and convert to float
    if isinstance(baseline_revenue, str):
        baseline_revenue = float(baseline_revenue.replace(",", ""))  # Remove commas and convert
    
    # Ensure that baseline_revenue is now a valid numeric value (float or int)
    if not isinstance(baseline_revenue, (int, float)):
        baseline_revenue = 739000000  # Default value if there's an issue with the revenue format
    
    # Now, use it in the Streamlit number input widget
        revenue_input = st.number_input("Baseline Revenue ($)", value=baseline_revenue, step=1000000)

    # Ensure revenue is a valid numeric value
    baseline_revenue = st.session_state.get("baseline_revenue", 739000000)
    
    # If it's a string (e.g., '1,000,000'), clean it and convert to float
    if isinstance(baseline_revenue, str):
        baseline_revenue = float(baseline_revenue.replace(",", ""))  # Remove commas and convert
     
    # Now, use it in the Streamlit number input widget
    revenue_input = st.number_input("Baseline Revenue ($)", value=baseline_revenue, step=1000000)
    
    # Ensure that revenue_input and session_state.baseline_revenue are of the same type
    if isinstance(revenue_input, (int, float)) and revenue_input != st.session_state.baseline_revenue:
        st.session_state.baseline_revenue = revenue_input    
    
    # Save the updated value back into session state
    if revenue_input != st.session_state.baseline_revenue:
        st.session_state.baseline_revenue = revenue_input   
        
    # Dynamically update input fields
        revenue_input = st.number_input("Baseline Revenue ($)", value=revenue, step=1000000)
        expense_input = st.number_input("IT Expense ($)", value=it_expense, step=100000)

    if revenue_input != revenue:
        st.session_state.baseline_revenue = revenue_input
    if 'it_expense' not in st.session_state:
        st.session_state.it_expense = 0  # Default value

    it_expense = st.session_state.it_expense
    expense_input = st.number_input("IT Expense ($)", value=it_expense, step=100000)
    
    if expense_input != it_expense:
        st.session_state.it_expense = expense_input
        
# Calculator Tab
if section == "📊 ITRM Calculator":
    st.title("📊 ITRM Multi-Year Calculator")

    if 'baseline_revenue' not in st.session_state:
        st.warning("Please configure inputs in the Inputs Setup tab first.")
        st.stop()

    # Retrieve the baseline and other inputs from session state
    baseline_revenue = st.session_state.baseline_revenue
    it_expense = st.session_state.it_expense
    category_expenses_to_total = st.session_state.category_expenses_to_total
    category_revenue_to_total = st.session_state.category_revenue_to_total
    revenue_growth = st.session_state.revenue_growth
    expense_growth = st.session_state.expense_growth

    # Display the baseline values
    st.markdown(f"### Baseline Revenue: ${baseline_revenue:,.2f}")
    st.markdown(f"### Baseline IT Expenses: ${it_expense:,.2f}")
    
    st.markdown("### Expense and Revenue Breakdown by Category")
    categories = ["Category 1", "Category 2", "Category 3", "Category 4", "Category 5"]
    category_expenses = []
    category_revenues = []
    
    # Input and Calculation for each category
    for i, category in enumerate(categories):
        col1, col2 = st.columns(2)
        with col1:
            expense_percent = category_expenses_to_total[i]
            st.markdown(f"{category} - **Expense %**: **{expense_percent * 100:.2f}%**")
        with col2:
            revenue_percent = category_revenue_to_total[i]
            st.markdown(f"{category} - **Revenue %**: **{revenue_percent * 100:.2f}%**")
        
        expense = it_expense * expense_percent
        revenue = baseline_revenue * revenue_percent
        category_expenses.append(expense)
        category_revenues.append(revenue)

    st.markdown("### Revenue Growth & Expense Growth")

    # Year 1 to 3 Revenue Growth and Expense Growth Calculation
    revenue_projection = {}
    expense_projection = {}
    
    for year in [1, 2, 3]:
        st.markdown(f"#### Year {year}")
        year_revenue = baseline_revenue * (1 + revenue_growth[year-1])
        year_expenses = it_expense * (1 + expense_growth[year-1])
        
        revenue_projection[f"Year {year}"] = year_revenue
        expense_projection[f"Year {year}"] = year_expenses
        
        st.markdown(f"**Projected Revenue for Year {year}:** ${year_revenue:,.2f}")
        st.markdown(f"**Projected Expenses for Year {year}:** ${year_expenses:,.2f}")

    st.markdown("---")
    
    # Total Expenses and Revenues for all categories combined
    total_expenses = sum(category_expenses)
    total_revenues = sum(category_revenues)
    
    st.markdown(f"### Total Expenses: ${total_expenses:,.2f}")
    st.markdown(f"### Total Revenues: ${total_revenues:,.2f}")
    
    # IT Revenue Margin Calculation (ITRM)
    itrm = (total_expenses / total_revenues) * 100 if total_revenues != 0 else 0
    st.markdown(f"### **IT Revenue Margin (ITRM):** {itrm:.2f}%")

    # Display Graph for the ITRM
    st.markdown("### 📈 ITRM Over Time")
    years = ['Year 1', 'Year 2', 'Year 3']
    itrms = [itrm, itrm, itrm]  # For now, assuming itrm remains the same for all 3 years, you can adjust this logic as needed

    fig, ax = plt.subplots()
    ax.plot(years, itrms, marker='o', linewidth=2)
    ax.set_ylabel("IT Revenue Margin (%)")
    ax.set_title("ITRM Over Time")
    st.pyplot(fig)

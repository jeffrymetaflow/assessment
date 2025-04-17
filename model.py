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

    if roadmap_items:
        st.subheader("📅 Strategic Timeline by Quarter")
        timeline_df = pd.DataFrame({
            "Quarter": ["Q1", "Q2", "Q3", "Q4"] * ((len(roadmap_items) + 3) // 4),
            "Action Item": roadmap_items[:16]
        })
        timeline_df = timeline_df.dropna().reset_index(drop=True)
        st.dataframe(timeline_df)

        st.subheader("✅ Progress Tracker")
        for quarter in ["Q1", "Q2", "Q3", "Q4"]:
            st.markdown(f"**{quarter}**")
            for item in timeline_df[timeline_df["Quarter"] == quarter]["Action Item"]:
                st.checkbox(f"{item[0]} – {item[1]}", key=f"{quarter}_{item[0]}")

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

# Calculator Tab
elif section == "📊 ITRM Calculator":
    st.title("📊 ITRM Multi-Year Calculator")
    if 'inputs' not in st.session_state:
        st.warning("Please configure inputs in the Inputs Setup tab first.")
        st.stop()

    inputs = st.session_state.inputs
    categories = ["Category 1", "Category 2", "Category 3", "Category 4", "Category 5"]
    revenue_input = {
        "Year 1": inputs['revenue_baseline'] * (1 + inputs['target_revenue_growth'][0]),
        "Year 2": inputs['revenue_baseline'] * (1 + inputs['target_revenue_growth'][1]),
        "Year 3": inputs['revenue_baseline'] * (1 + inputs['target_revenue_growth'][2]),
    }
    default_changes = {
        "Year 1": [0.30, -0.20, -0.15, 0.10, 0.10],
        "Year 2": [0.05, -0.02, -0.20, 0.10, 0.05],
        "Year 3": [0.05, -0.02, -0.20, 0.10, 0.05],
    }

    expense_results = {}
    for year in ["Year 1", "Year 2", "Year 3"]:
        st.markdown(f"#### {year} Adjustments")
        category_expenses, split_total = [], 0
        revenue = revenue_input[year]

        for i, cat in enumerate(categories):
            col1, col2 = st.columns(2)
            with col1:
                split = inputs['category_revenue_split'][i]
                st.markdown(f"{cat} Revenue %: **{split*100:.1f}%**")
            with col2:
                change = st.number_input(f"{cat} Expense Change % ({year})", format="%.2f", value=default_changes[year][i], key=f"calc_{year}_{cat}_change")
            split_total += split
            expense = revenue * split * (1 + change)
            category_expenses.append(expense)

        if abs(split_total - 1.0) > 0.001:
            st.error(f"{year} revenue splits do not total 100% (currently {split_total*100:.2f}%)")
            continue

        total_expense = sum(category_expenses)
        itrm = (total_expense / revenue) * 100
        expense_results[year] = {
            "category_expenses": category_expenses,
            "Total Expense": total_expense,
            "ITRM": itrm
        }
        st.success(f"**{year} Total Expense:** ${total_expense:,.2f}")
        st.info(f"**{year} IT Revenue Margin (ITRM):** {itrm:.2f}%")

    st.session_state.calculator_results = expense_results

    if expense_results:
        st.markdown("---")
        st.subheader("📈 ITRM Trend")
        years = list(expense_results.keys())
        itrms = [expense_results[y]["ITRM"] for y in years]
        fig, ax = plt.subplots()
        ax.plot(years, itrms, marker='o', linewidth=2)
        ax.set_ylabel("IT Revenue Margin (%)")
        ax.set_title("ITRM Over Time")
        st.pyplot(fig)

        st.markdown("---")
        st.subheader("🧠 Summary Insights")
        itrm_start = expense_results["Year 1"]["ITRM"]
        itrm_end = expense_results["Year 3"]["ITRM"]
        delta = itrm_start - itrm_end

        if delta > 0:
            st.success(f"✅ Over the modeled period, your IT Revenue Margin improved by {delta:.2f}%.")
            st.write("This indicates increased efficiency and optimization of IT resources relative to revenue growth.")
        elif delta < 0:
            st.warning(f"⚠️ IT Revenue Margin worsened by {-delta:.2f}%.")
            st.write("This may indicate IT cost growth outpacing revenue or ineffective optimization.")
        else:
            st.info("ℹ️ IT Revenue Margin remained consistent across the modeling period.")

        st.markdown("**Key Observations:**")
        st.markdown("- Monitor expense-heavy categories for targeted optimization.")
        st.markdown("- Validate whether revenue growth assumptions are realistic.")
        st.markdown("- Revisit automation or cloud strategies to reduce total IT spend.")

# Financial Summary Tab
elif section == "💰 ITRM Financial Summary":
    st.title("💰 ITRM Financial Summary")

    if 'inputs' not in st.session_state:
        st.warning("Please set up your inputs in the Inputs Setup tab.")
        st.stop()
    if 'calculator_results' not in st.session_state:
        st.warning("Please run the calculator to populate financial data.")
        st.stop()

    inputs = st.session_state.inputs
    results = st.session_state.calculator_results
    categories = ["Category 1", "Category 2", "Category 3", "Category 4", "Category 5"]

    st.subheader("📊 Category Financial Breakdown (Year 3)")
    year = "Year 3"
    revenue = inputs['revenue_baseline'] * (1 + inputs['target_revenue_growth'][2])
    cat_data = []
    for i, cat in enumerate(categories):
        split = inputs['category_revenue_split'][i]
        expense = results[year]['category_expenses'][i]
        percent_exp = expense / results[year]['Total Expense'] * 100
        percent_rev = split * 100
        cat_data.append([cat, expense, percent_exp, percent_rev])

    cat_df = pd.DataFrame(cat_data, columns=["Category", "Total IT Expense", "% of Expense", "% of Revenue"])
    cat_df["Total IT Expense"] = cat_df["Total IT Expense"].apply(lambda x: f"${x:,.2f}")
    cat_df["% of Expense"] = cat_df["% of Expense"].apply(lambda x: f"{x:.2f}%")
    cat_df["% of Revenue"] = cat_df["% of Revenue"].apply(lambda x: f"{x:.2f}%")
    st.dataframe(cat_df)

    fig, ax = plt.subplots()
    ax.bar(cat_df["Category"], cat_df["% of Expense"], label="% of Expense")
    ax.bar(cat_df["Category"], cat_df["% of Revenue"], alpha=0.5, label="% of Revenue")
    ax.set_title("Expense vs Revenue Distribution by Category")
    ax.set_ylabel("%")
    ax.legend()
    st.pyplot(fig)

    st.subheader("📈 Revenue & Expense Growth Targets")
    growth_df = pd.DataFrame({
        "Metric": ["Revenue Growth", "Expense Growth"],
        "Year 1": [inputs['target_revenue_growth'][0], inputs['target_expense_growth'][0]],
        "Year 2": [inputs['target_revenue_growth'][1], inputs['target_expense_growth'][1]],
        "Year 3": [inputs['target_revenue_growth'][2], inputs['target_expense_growth'][2]]
    })
    st.dataframe(growth_df)

    st.subheader("🧠 Summary Insights")
    top_exp = cat_df.sort_values("% of Expense", ascending=False).iloc[0]
    top_rev = cat_df.sort_values("% of Revenue", ascending=False).iloc[0]

    st.markdown(f"- **{top_exp['Category']}** has the highest share of IT expenses: **{top_exp['% of Expense']}**")
    st.markdown(f"- **{top_rev['Category']}** contributes the most to revenue: **{top_rev['% of Revenue']}**")

    if top_exp['Category'] != top_rev['Category']:
        st.warning("🚨 The top IT expense category does not align with top revenue category. Consider optimization.")
    else:
        st.success("✅ Top IT spending aligns with top revenue driver, indicating strategic alignment.")

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

# Inputs Tab
elif section == "⚙️ Inputs Setup":
    if 'inputs' not in st.session_state:
        st.session_state.inputs = {
            'revenue_baseline': 739_000_000,
            'it_expense_baseline': 4_977_370,
            'category_revenue_split': [0.5, 0.2, 0.1, 0.15, 0.05],
            'category_expense_split': [0.25, 0.2, 0.1, 0.1, 0.35],
            'target_revenue_growth': [0.10, 0.05, 0.07],
            'target_expense_growth': [0.06, 0.03, 0.03]
        }

    st.title("⚙️ ITRM Inputs Setup")
    st.session_state.inputs['revenue_baseline'] = st.number_input("Baseline Revenue ($)", value=st.session_state.inputs['revenue_baseline'], key="inputs_revenue_baseline")
    st.session_state.inputs['it_expense_baseline'] = st.number_input("Baseline IT Expense ($)", value=st.session_state.inputs['it_expense_baseline'], key="inputs_it_expense_baseline")

    st.subheader("Application Category Splits")
    categories = ["Category 1", "Category 2", "Category 3", "Category 4", "Category 5"]
    revenue_splits, expense_splits = [], []
    for i, cat in enumerate(categories):
        col1, col2 = st.columns(2)
        with col1:
            rev = st.number_input(f"{cat} - % of Revenue", min_value=0.0, max_value=1.0, value=st.session_state.inputs['category_revenue_split'][i], key=f"inputs_{cat}_rev")
            revenue_splits.append(rev)
        with col2:
            exp = st.number_input(f"{cat} - % of Expense", min_value=0.0, max_value=1.0, value=st.session_state.inputs['category_expense_split'][i], key=f"inputs_{cat}_exp")
            expense_splits.append(exp)
    st.session_state.inputs['category_revenue_split'] = revenue_splits
    st.session_state.inputs['category_expense_split'] = expense_splits

    st.subheader("Target Revenue & Expense Growth")
    rev_growth, exp_growth = [], []
    for i, year in enumerate(["Year 1", "Year 2", "Year 3"]):
        col1, col2 = st.columns(2)
        with col1:
            rev = st.number_input(f"{year} Target Revenue Growth (%)", format="%.2f", value=st.session_state.inputs['target_revenue_growth'][i], key=f"inputs_{year}_rev_growth")
            rev_growth.append(rev)
        with col2:
            exp = st.number_input(f"{year} Target Expense Growth (%)", format="%.2f", value=st.session_state.inputs['target_expense_growth'][i], key=f"inputs_{year}_exp_growth")
            exp_growth.append(exp)
    st.session_state.inputs['target_revenue_growth'] = rev_growth
    st.session_state.inputs['target_expense_growth'] = exp_growth
    st.success("Inputs saved in session state. You can now use them in the calculator tab.")

# Calculator Tab
elif section == "📊 ITRM Calculator":
    st.title("📊 ITRM Multi-Year Calculator")
    if 'inputs' not in st.session_state:
        st.warning("Please configure inputs in the Inputs Setup tab first.")
        st.stop()

    inputs = st.session_state.inputs
    categories = ["Category 1", "Category 2", "Category 3", "Category 4", "Category 5"]
    revenue_input = {
        "Year 1": inputs['revenue_baseline'] * (1 + inputs['target_revenue_growth'][0]),
        "Year 2": inputs['revenue_baseline'] * (1 + inputs['target_revenue_growth'][1]),
        "Year 3": inputs['revenue_baseline'] * (1 + inputs['target_revenue_growth'][2]),
    }
    default_changes = {
        "Year 1": [0.30, -0.20, -0.15, 0.10, 0.10],
        "Year 2": [0.05, -0.02, -0.20, 0.10, 0.05],
        "Year 3": [0.05, -0.02, -0.20, 0.10, 0.05],
    }

    expense_results = {}
    for year in ["Year 1", "Year 2", "Year 3"]:
        st.markdown(f"#### {year} Adjustments")
        category_expenses, split_total = [], 0
        revenue = revenue_input[year]

        for i, cat in enumerate(categories):
            col1, col2 = st.columns(2)
            with col1:
                split = inputs['category_revenue_split'][i]
                st.markdown(f"{cat} Revenue %: **{split*100:.1f}%**")
            with col2:
                change = st.number_input(f"{cat} Expense Change % ({year})", format="%.2f", value=default_changes[year][i], key=f"calc_{year}_{cat}_change")
            split_total += split
            expense = revenue * split * (1 + change)
            category_expenses.append(expense)

        if abs(split_total - 1.0) > 0.001:
            st.error(f"{year} revenue splits do not total 100% (currently {split_total*100:.2f}%)")
            continue

        total_expense = sum(category_expenses)
        itrm = (total_expense / revenue) * 100
        expense_results[year] = {"Total Expense": total_expense, "ITRM": itrm}
        st.success(f"**{year} Total Expense:** ${total_expense:,.2f}")
        st.info(f"**{year} IT Revenue Margin (ITRM):** {itrm:.2f}%")

    if expense_results:
        st.markdown("---")
        st.subheader("📈 ITRM Trend")
        years = list(expense_results.keys())
        itrms = [expense_results[y]["ITRM"] for y in years]
        fig, ax = plt.subplots()
        ax.plot(years, itrms, marker='o', linewidth=2)
        ax.set_ylabel("IT Revenue Margin (%)")
        ax.set_title("ITRM Over Time")
        st.pyplot(fig)

        st.markdown("---")
        st.subheader("🧠 Summary Insights")
        first_year = years[0]
        last_year = years[-1]
        itrm_start = expense_results[first_year]["ITRM"]
        itrm_end = expense_results[last_year]["ITRM"]
        delta = itrm_start - itrm_end

        if delta > 0:
            st.success(f"✅ Over the modeled period, your IT Revenue Margin improved by {delta:.2f}%.")
            st.write("This indicates increased efficiency and optimization of IT resources relative to revenue growth.")
        elif delta < 0:
            st.warning(f"⚠️ IT Revenue Margin worsened by {-delta:.2f}%.")
            st.write("This may indicate IT cost growth outpacing revenue or ineffective optimization.")
        else:
            st.info("ℹ️ IT Revenue Margin remained consistent across the modeling period.")

        st.markdown("**Key Observations:**")
        st.markdown("- Monitor expense-heavy categories for targeted optimization.")
        st.markdown("- Validate whether revenue growth assumptions are realistic.")
        st.markdown("- Revisit automation or cloud strategies to reduce total IT spend.")


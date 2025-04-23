import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import uuid
import numpy as np

# Sidebar Navigation
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", [
    "🧠 Overview Summary",
    "⚙️ Inputs Setup",
    "📊 ITRM Calculator",
    "💰 ITRM Financial Summary",

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

if section == "🧠 Overview Summary":
    st.title("Overview of IT Revenue Margin")
    st.markdown("""
    Welcome to the IT Revenue Margin (ITRM) Dashboard. Here you will find an overview of the revenue, expenses, and IT maturity for your company.
    """)

    # Client name input
    client_name = st.text_input("Enter Client Name:", "Acme Corp")
    st.markdown(f"**Client Name:** {client_name}")

    # ITRM Score
    itrm_score = st.number_input("Overall IT Revenue Margin Score", min_value=0, max_value=100, value=75, step=1)
    st.markdown(f"**ITRM Score:** {itrm_score}%")
    
    # Revenue and Expense Growth
    st.subheader("Revenue and Expense Growth Over Time")
    years = ['Year 1', 'Year 2', 'Year 3']
    revenue = [8000000000, 8500000000, 9000000000]  # Example revenue data
    expenses = [150000000, 160000000, 170000000]   # Example expense data

    fig, ax = plt.subplots()
    ax.plot(years, revenue, label="Revenue", color='blue')
    ax.plot(years, expenses, label="Expenses", color='red')
    ax.set_xlabel("Years")
    ax.set_ylabel("Amount ($)")
    ax.legend()
    st.pyplot(fig)

    # IT Maturity Heatmap
    # IT Maturity Heatmap (Matplotlib version)
    st.subheader("IT Maturity Scores")
    maturity_scores = pd.DataFrame({
        'Category': ['Performance', 'Security', 'Compliance', 'Cost Efficiency', 'Innovation'],
        'Score (%)': [80, 70, 60, 90, 75]
    })
    
    fig, ax = plt.subplots(figsize=(8, 4))
    cax = ax.matshow([maturity_scores['Score (%)'].values], cmap='coolwarm')
    
    # Add color bar
    fig.colorbar(cax)
    
    # Set the x-ticks and labels
    ax.set_xticks(range(len(maturity_scores['Category'])))
    ax.set_xticklabels(maturity_scores['Category'], rotation=45, ha='right')
    
    ax.set_title("IT Maturity Heatmap")
    st.pyplot(fig)

    # AI Assistant Recommendations
    st.subheader("AI-Powered Recommendations")
    st.markdown("""
    Based on your inputs, the AI Assistant recommends the following actions to improve IT maturity and revenue margin:
    - **Increase Automation** in IT processes.
    - **Focus on Cybersecurity** to mitigate risks.
    - **Optimize IT Costs** to improve profitability.
    """)     

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
    # Revenue Growth & Expense Growth Sliders
    revenue_growth = []
    for i in range(3):
        growth = st.slider(
            f"Year {i+1} Growth Rate (%)",
            min_value=0.0,
            max_value=100.0,
            value=5.0,
            key=f"revenue_growth_slider_{i}"  # Unique key
        )
        revenue_growth.append(growth)
    expense_growth = []
    for i in range(3):
        growth = st.slider(
            f"Year {i+1} Expense Growth (%)",
            min_value=0.0,
            max_value=100.0,
            value=3.0,
            key=f"expense_growth_slider_{i}"  # Unique key
        )
        expense_growth.append(growth)
    
    # Ensure revenue_input exists
    if "revenue_input" not in st.session_state:
        st.error("Please configure the inputs in the 'ITRM Calculator' tab first.")
        st.stop()
    
    # Retrieve revenue_input
    revenue_input = st.session_state.revenue_input
    
    # Projected Revenue Calculation
    projected_revenue = {}
    for i, year in enumerate(revenue_input.keys()):
        growth_percentage = revenue_growth[i] / 100
        if i == 0:
            projected_revenue[year] = revenue_input[year]
        else:
            previous_year = list(revenue_input.keys())[i - 1]
            projected_revenue[year] = (
                projected_revenue[previous_year] * (1 + growth_percentage)
            )
    
    # Display the projected revenue
    st.write("Projected Revenue:", projected_revenue)
       
    # Ensure expense_input exists
    if "expense_input" not in st.session_state:
        st.error("Please configure the inputs in the 'ITRM Calculator' tab first.")
        st.stop()
    
    # Retrieve expense_input
    expense_input = st.session_state.expense_input

    # Projected Expenses Calculation
    projected_expenses = {}
    for i, year in enumerate(expense_input.keys()):
        growth_percentage = expense_growth[i] / 100
        if i == 0:
            projected_expenses[year] = expense_input[year]
        else:
            projected_expenses[year] = projected_expenses[f"Year {i}"] * (1 + growth_percentage)

    # Display the projected expenses
    st.write("Projected Expenses:", projected_expenses)    
    
    # Display Calculated Revenue and Expenses for Each Year
    st.markdown(f"Year 1 Projected Revenue: ${projected_revenue['Year 1']:,}")
    st.markdown(f"Year 2 Projected Revenue: ${projected_revenue['Year 2']:,}")
    st.markdown(f"Year 3 Projected Revenue: ${projected_revenue['Year 3']:,}")
    
    st.markdown(f"Year 1 Projected Expenses: ${projected_expenses['Year 1']:,}")
    st.markdown(f"Year 2 Projected Expenses: ${projected_expenses['Year 2']:,}")
    st.markdown(f"Year 3 Projected Expenses: ${projected_expenses['Year 3']:,}") 
    
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

    # Year-over-Year Comparison
    st.markdown("### 📊 Year-over-Year Comparison")
    revenue_values = [projected_revenue["Year 1"], projected_revenue["Year 2"], projected_revenue["Year 3"]]
    expense_values = [projected_expenses["Year 1"], projected_expenses["Year 2"], projected_expenses["Year 3"]]

    fig2, ax2 = plt.subplots(figsize=(8, 6))
    ax2.bar(years, revenue_values, color='green', alpha=0.6, label='Projected Revenue')
    ax2.bar(years, expense_values, color='red', alpha=0.6, label='Projected Expenses')

    ax2.set_xlabel('Year')
    ax2.set_ylabel('Amount ($)')
    ax2.set_title('Year-over-Year Comparison of Revenue and Expenses')
    ax2.legend()

    st.pyplot(fig2)

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

    # Example in the ITRM Calculator tab
    if section == "📊 ITRM Calculator":
        st.title("📊 ITRM Multi-Year Calculator")
    
        # Retrieve baseline revenue and inputs
        baseline_revenue = st.number_input("Baseline Revenue ($)", min_value=0.0)
        revenue_growth = [st.slider(f"Year {i+1} Revenue Growth (%)", 0.0, 100.0, 5.0) for i in range(3)]
    
        # Define revenue input based on baseline revenue and years
        revenue_input = {
            f"Year {i+1}": baseline_revenue * (1 + sum([revenue_growth[j] / 100 for j in range(i)]))
            for i in range(3)
        }
    
        # Save to session state
        st.session_state.revenue_input = revenue_input
        st.session_state.revenue_growth = revenue_growth

    if section == "📊 ITRM Calculator":
        st.title("📊 ITRM Multi-Year Calculator")
    
        # Get baseline IT expense and growth inputs
        baseline_expense = st.number_input("Baseline Expense ($)", min_value=0, step=1000)
        expense_growth = [st.slider(f"Year {i+1} Expense Growth (%)", 0.0, 100.0, 3.0) for i in range(3)]
    
        # Define expense input as a dictionary
        expense_input = {
            f"Year {i+1}": baseline_expense * (1 + sum([expense_growth[j] / 100 for j in range(i)]))
            for i in range(3)
        }
    
        # Save to session state
        st.session_state.expense_input = expense_input
        st.session_state.expense_growth = expense_growth

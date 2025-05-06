import pandas as pd
import streamlit as st

class ITRMController:
    def __init__(self):
        self.components = []
        self.edges = []
        self.simulation_results = {}
        self.forecast_model = {}
        self.financial_summary = {}

    def __init__(self, revenue=5_000_000):
        self.revenue = revenue    
    
    def get_components(self):
            return self.components

    def set_components(self, components_list):
        self.components = components_list
    
    def add_component(self, component):
        self.components.append(component)

    def add_edge(self, source, target):
        self.edges.append((source, target))

    def run_simulation(self):
        # Estimate revenue at risk using a simple model
        risk_data = []
        for c in self.components:
            revenue_at_risk = (c["Revenue Impact %"] * c["Risk Score"]) / 100
            risk_data.append({
                "Component": c["Name"],
                "Revenue at Risk (%)": revenue_at_risk
            })
        self.simulation_results = pd.DataFrame(risk_data)

    def generate_forecast(self):
        self.forecast_model = {"2024": 0.25, "2025": 0.28, "2026": 0.31}

    def summarize_financials(self):
        total_spend = sum(c["Spend"] for c in self.components)
        avg_revenue = sum(c["Revenue Impact %"] for c in self.components) / len(self.components)
        avg_risk = sum(c["Risk Score"] for c in self.components) / len(self.components)
        self.financial_summary = {
            "Total Spend": total_spend,
            "Avg Revenue Support": avg_revenue,
            "Avg Risk": avg_risk
        }

    def get_category_aggregates(self):
        aggregates = {}
        for comp in self.components:
            category = comp.get("Category")
            spend = comp.get("Spend", 0)
            revenue_impact = comp.get("Revenue Impact %", 0)

            if category not in aggregates:
                aggregates[category] = {"spend": 0, "revenue_impact": 0}

            aggregates[category]["spend"] += spend
            aggregates[category]["revenue_impact"] += revenue_impact

        return aggregates

    def get_ai_context(self):
        return {
            "components": self.components,
            "simulation": self.simulation_results.to_dict(),
            "forecast": self.forecast_model,
            "summary": self.financial_summary
        }

    def get_category_risk_summary(self):
        category_risk = {}
        for comp in self.components:
            cat = comp.get("Category", "Unknown")
            risk_score = comp.get("Risk Score", 0)
            revenue_pct = comp.get("Revenue Impact %", 0)
            risk_val = (revenue_pct * risk_score) / 100
    
            if cat not in category_risk:
                category_risk[cat] = {"total_risk": 0, "components": []}
    
            category_risk[cat]["total_risk"] += risk_val
            category_risk[cat]["components"].append({
                "Name": comp.get("Name", ""),
                "Revenue Impact %": revenue_pct,
                "Risk Score": risk_score,
                "Revenue at Risk (%)": round(risk_val, 2)
            })
    
        return category_risk

    def get_baseline_revenue(self):
        return getattr(self, "baseline_revenue", st.session_state.get("revenue", 0))

    def get_category_impact_percentages(self):
        """Returns a dictionary mapping category -> assigned revenue impact %"""
        category_map = {}
        for comp in self.components:
            cat = comp.get("Category")
            impact = comp.get("Revenue Impact %")
            if cat and isinstance(impact, (int, float)):
                if cat in category_map:
                    category_map[cat].append(impact)
                else:
                    category_map[cat] = [impact]
    
        # Average across components for each category
        return {cat: sum(vals)/len(vals) for cat, vals in category_map.items()}

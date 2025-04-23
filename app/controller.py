import pandas as pd

class ITRMController:
    def __init__(self):
        self.components = []
        self.edges = []
        self.simulation_results = {}
        self.forecast_model = {}
        self.financial_summary = {}

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

    def get_ai_context(self):
        return {
            "components": self.components,
            "simulation": self.simulation_results.to_dict(),
            "forecast": self.forecast_model,
            "summary": self.financial_summary
        }

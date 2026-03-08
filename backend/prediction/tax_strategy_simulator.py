from typing import Dict, Any, List


class TaxStrategySimulator:
    """
    Simulates possible tax optimization strategies.
    """

    def simulate(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:

        strategies = []

        income = data.get("predicted_income", 0)

        retirement_contribution = income * 0.05

        strategies.append({
            "strategy": "increase_401k_contribution",
            "recommended_amount": retirement_contribution,
            "estimated_tax_savings": retirement_contribution * 0.22
        })

        strategies.append({
            "strategy": "itemize_deductions",
            "estimated_tax_savings": 500
        })

        return strategies

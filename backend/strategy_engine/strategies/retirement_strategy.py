from typing import List, Dict
from ..savings_estimator import SavingsEstimator


def generate(context) -> List[Dict]:

    income = context.get("predicted_income", 0)
    tax_rate = context.get("effective_tax_rate", 0.22)

    contribution = income * 0.05

    savings = SavingsEstimator.estimate_retirement_savings(contribution, tax_rate)

    return [{
        "strategy": "increase_401k",
        "amount": round(contribution, 2),
        "estimated_savings": savings,
        "confidence": 0.85
    }]

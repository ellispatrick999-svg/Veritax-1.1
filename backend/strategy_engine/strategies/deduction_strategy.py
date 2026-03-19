from typing import List, Dict
from ..savings_estimator import SavingsEstimator


def generate(context) -> List[Dict]:

    deductions = context.get("total_deductions", 0)
    tax_rate = context.get("effective_tax_rate", 0.22)

    savings = SavingsEstimator.estimate_deduction_savings(deductions, tax_rate)

    return [{
        "strategy": "itemize_deductions",
        "estimated_savings": savings,
        "confidence": 0.8
    }]

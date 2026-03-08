from typing import Dict, Any
from .base_model import PredictionModel


class TaxLiabilityPredictor(PredictionModel):
    """
    Estimates federal tax liability using simplified tax brackets.
    """

    FEDERAL_BRACKETS = [
        (0, 0.10),
        (11000, 0.12),
        (44725, 0.22),
        (95375, 0.24),
        (182100, 0.32),
    ]

    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:

        income = data.get("predicted_income", 0)
        deductions = data.get("total_deductions", 0)

        taxable_income = max(0, income - deductions)

        tax = 0

        for bracket, rate in self.FEDERAL_BRACKETS:
            if taxable_income > bracket:
                tax += (taxable_income - bracket) * rate
                taxable_income = bracket

        return {
            "estimated_federal_tax": round(tax, 2),
        }

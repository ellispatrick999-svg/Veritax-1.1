from typing import Dict, Any
from .base_model import PredictionModel


class CreditEligibilityPredictor(PredictionModel):
    """
    Predicts eligibility for common tax credits.
    """

    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:

        income = data.get("predicted_income", 0)
        dependents = data.get("dependents", 0)

        credits = {}

        if dependents > 0:
            credits["child_tax_credit"] = dependents * 2000

        if income < 60000:
            credits["earned_income_tax_credit"] = 1000

        return {
            "eligible_credits": credits,
            "total_credits": sum(credits.values())
        }

from typing import Dict, Any
from .base_model import PredictionModel


class DeductionEstimator(PredictionModel):
    """
    Estimates likely tax deductions based on user financial data.
    """

    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:

        deductions = {}

        if data.get("mortgage_interest"):
            deductions["mortgage_interest"] = data["mortgage_interest"]

        if data.get("charitable_donations"):
            deductions["charitable_donations"] = data["charitable_donations"]

        if data.get("business_expenses"):
            deductions["business_expenses"] = data["business_expenses"]

        total = sum(deductions.values())

        return {
            "predicted_deductions": deductions,
            "total_deductions": total
        }

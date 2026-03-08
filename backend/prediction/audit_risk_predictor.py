from typing import Dict, Any
from .base_model import PredictionModel


class AuditRiskPredictor(PredictionModel):
    """
    Estimates IRS audit risk based on financial patterns.
    """

    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:

        income = data.get("predicted_income", 0)
        deductions = data.get("total_deductions", 0)

        deduction_ratio = deductions / income if income else 0

        risk_score = min(1.0, deduction_ratio * 0.5)

        return {
            "audit_risk_score": round(risk_score, 3)
        }

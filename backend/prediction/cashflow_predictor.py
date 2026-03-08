from typing import Dict, Any
from .base_model import PredictionModel


class CashflowPredictor(PredictionModel):
    """
    Predicts monthly cash surplus or deficit.
    """

    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:

        monthly_income = data.get("monthly_income", 0)
        monthly_expenses = data.get("monthly_expenses", 0)

        surplus = monthly_income - monthly_expenses

        return {
            "monthly_surplus": surplus,
            "cashflow_status": "positive" if surplus >= 0 else "negative"
        }

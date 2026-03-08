import numpy as np
from typing import Dict, Any
from .base_model import PredictionModel


class IncomeForecast(PredictionModel):
    """
    Forecasts next year's income using historical income data.
    """

    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        income_history = data.get("income_history", [])

        if not income_history:
            raise ValueError("Income history is required")

        mean_income = float(np.mean(income_history))
        volatility = float(np.std(income_history))

        next_year_prediction = mean_income + (volatility * 0.1)

        return {
            "predicted_income_next_year": round(next_year_prediction, 2),
            "income_volatility": round(volatility, 2),
        }

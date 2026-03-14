import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class SavingsRatePrediction:
    realistic_savings_rate: float
    historical_savings_rate: float
    income_volatility_penalty: float
    spending_stability_score: float
    metadata: Dict[str, Any]


class SavingsRatePredictor:
    """
    Predicts a realistic savings rate based on historical income, spending,
    volatility, and behavioral consistency. Supports optional ML-based adjustments.
    """

    def __init__(
        self,
        min_months: int = 6,
        volatility_weight: float = 0.4,
        stability_weight: float = 0.3,
        ml_model: Optional[Any] = None,
    ):
        self.min_months = min_months
        self.volatility_weight = volatility_weight
        self.stability_weight = stability_weight
        self.ml_model = ml_model

    def _compute_historical_savings_rate(
        self, income: pd.Series, spending: pd.Series
    ) -> float:
        savings = income - spending
        avg_income = max(income.mean(), 1e-6)
        return float(savings.mean() / avg_income)

    def _compute_income_volatility_penalty(self, income: pd.Series) -> float:
        std = float(income.std())
        mean = max(float(income.mean()), 1e-6)
        cv = std / mean
        return min(1.0, cv)

    def _compute_spending_stability(self, spending: pd.Series) -> float:
        std = float(spending.std())
        mean = max(float(spending.mean()), 1e-6)
        cv = std / mean
        return float(1.0 - min(1.0, cv))

    def _ml_adjustment(self, features: Dict[str, float]) -> float:
        if self.ml_model is None:
            return 0.0
        df = pd.DataFrame([features])
        return float(self.ml_model.predict(df)[0])

    def predict(
        self,
        monthly_income: pd.Series,
        monthly_spending: pd.Series,
    ) -> SavingsRatePrediction:

        if len(monthly_income) < self.min_months or len(monthly_spending) < self.min_months:
            raise ValueError(f"At least {self.min_months} months of data are required.")

        monthly_income = monthly_income.sort_index()
        monthly_spending = monthly_spending.sort_index()

        historical_rate = self._compute_historical_savings_rate(
            monthly_income, monthly_spending
        )
        volatility_penalty = self._compute_income_volatility_penalty(monthly_income)
        spending_stability = self._compute_spending_stability(monthly_spending)

        base_rate = (
            historical_rate
            * (1 - self.volatility_weight)
            * (1 + self.stability_weight * spending_stability)
        )

        ml_adjustment = self._ml_adjustment(
            {
                "historical_rate": historical_rate,
                "volatility_penalty": volatility_penalty,
                "spending_stability": spending_stability,
                "mean_income": float(monthly_income.mean()),
            }
        )

        realistic_rate = max(0.0, min(1.0, base_rate - volatility_penalty + ml_adjustment))

        return SavingsRatePrediction(
            realistic_savings_rate=float(realistic_rate),
            historical_savings_rate=float

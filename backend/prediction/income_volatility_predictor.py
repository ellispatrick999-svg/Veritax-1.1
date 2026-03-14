import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class VolatilityResult:
    volatility_score: float
    monthly_std: float
    coefficient_of_variation: float
    trend_direction: float
    metadata: Dict[str, Any]


class IncomeVolatilityPredictor:
    """
    Predicts how unstable a user's income is over time.
    Works with raw transaction data or pre-aggregated monthly income.
    """

    def __init__(
        self,
        min_months: int = 6,
        smoothing: bool = True,
        ml_model: Optional[Any] = None,
    ):
        self.min_months = min_months
        self.smoothing = smoothing
        self.ml_model = ml_model

    def _smooth(self, series: pd.Series) -> pd.Series:
        if not self.smoothing or len(series) < 3:
            return series
        return series.rolling(window=3, min_periods=1).mean()

    def _compute_trend(self, series: pd.Series) -> float:
        if len(series) < 2:
            return 0.0
        x = np.arange(len(series))
        slope = np.polyfit(x, series.values, 1)[0]
        return float(slope)

    def _compute_volatility(self, series: pd.Series) -> Dict[str, float]:
        monthly_std = float(series.std())
        mean_income = float(series.mean()) if series.mean() != 0 else 1e-6
        coefficient_of_variation = monthly_std / mean_income
        return {
            "monthly_std": monthly_std,
            "coefficient_of_variation": coefficient_of_variation,
        }

    def _ml_adjustment(self, features: Dict[str, float]) -> float:
        if self.ml_model is None:
            return 0.0
        df = pd.DataFrame([features])
        return float(self.ml_model.predict(df)[0])

    def predict(self, monthly_income: pd.Series) -> VolatilityResult:
        if len(monthly_income) < self.min_months:
            raise ValueError(
                f"At least {self.min_months} months of income data are required."
            )

        monthly_income = monthly_income.sort_index()
        smoothed = self._smooth(monthly_income)

        trend = self._compute_trend(smoothed)
        vol = self._compute_volatility(smoothed)

        base_score = (
            vol["coefficient_of_variation"] * 0.7
            + abs(trend) * 0.3
        )

        ml_adjustment = self._ml_adjustment(
            {
                "std": vol["monthly_std"],
                "cv": vol["coefficient_of_variation"],
                "trend": trend,
                "months": len(smoothed),
            }
        )

        final_score = max(0.0, min(1.0, base_score + ml_adjustment))

        return VolatilityResult(
            volatility_score=final_score,
            monthly_std=vol["monthly_std"],
            coefficient_of_variation=vol["coefficient_of_variation"],
            trend_direction=trend,
            metadata={
                "smoothed": smoothed.tolist(),
                "raw_months": len(monthly_income),
                "ml_adjustment": ml_adjustment,
            },
        )

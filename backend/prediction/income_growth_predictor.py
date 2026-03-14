import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class IncomeGrowthForecast:
    projected_growth_rate: float
    historical_growth_rate: float
    trend_slope: float
    forecasted_income_next_month: float
    metadata: Dict[str, Any]


class IncomeGrowthPredictor:
    """
    Forecasts future income growth using historical income data.
    Supports linear trend modeling, exponential smoothing, and optional ML-based adjustments.
    """

    def __init__(
        self,
        min_months: int = 6,
        smoothing_alpha: float = 0.3,
        ml_model: Optional[Any] = None,
    ):
        self.min_months = min_months
        self.smoothing_alpha = smoothing_alpha
        self.ml_model = ml_model

    def _exponential_smoothing(self, series: pd.Series) -> pd.Series:
        smoothed = [series.iloc[0]]
        for value in series.iloc[1:]:
            smoothed.append(self.smoothing_alpha * value + (1 - self.smoothing_alpha) * smoothed[-1])
        return pd.Series(smoothed, index=series.index)

    def _compute_historical_growth(self, series: pd.Series) -> float:
        if len(series) < 2:
            return 0.0
        start = float(series.iloc[0])
        end = float(series.iloc[-1])
        return (end - start) / max(start, 1e-6)

    def _compute_trend_slope(self, series: pd.Series) -> float:
        if len(series) < 2:
            return 0.0
        x = np.arange(len(series))
        slope = np.polyfit(x, series.values, 1)[0]
        return float(slope)

    def _forecast_next_month(self, series: pd.Series, slope: float) -> float:
        return float(series.iloc[-1] + slope)

    def _ml_adjustment(self, features: Dict[str, float]) -> float:
        if self.ml_model is None:
            return 0.0
        df = pd.DataFrame([features])
        return float(self.ml_model.predict(df)[0])

    def predict(self, monthly_income: pd.Series) -> IncomeGrowthForecast:
        if len(monthly_income) < self.min_months:
            raise ValueError(
                f"At least {self.min_months} months of income data are required."
            )

        monthly_income = monthly_income.sort_index()
        smoothed = self._exponential_smoothing(monthly_income)

        historical_growth = self._compute_historical_growth(smoothed)
        trend_slope = self._compute_trend_slope(smoothed)
        forecast_next_month = self._forecast_next_month(smoothed, trend_slope)

        base_growth_rate = (
            historical_growth * 0.6 +
            (trend_slope / max(smoothed.mean(), 1e-6)) * 0.4
        )

        ml_adjustment = self._ml_adjustment(
            {
                "historical_growth": historical_growth,
                "trend_slope": trend_slope,
                "mean_income": float(smoothed.mean()),
                "months": len(smoothed),
            }
        )

        projected_growth_rate = base_growth_rate + ml_adjustment

        return IncomeGrowthForecast(
            projected_growth_rate=float(projected_growth_rate),
            historical_growth_rate=float(historical_growth),
            trend_slope=float(trend_slope),
            forecasted_income_next_month=float(forecast_next_month),
            metadata={
                "smoothed_series": smoothed.tolist(),
                "ml_adjustment": ml_adjustment,
                "raw_months": len(monthly_income),
            },
        )

import pandas as pd
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class CreditValuePrediction:
    estimated_value: float
    eligibility_probability: float
    rule_based_value: float
    ml_adjustment: float
    metadata: Dict[str, Any]


class CreditValuePredictor:
    """
    Predicts the total expected value of a tax credit, not just eligibility.
    Combines rule-based phase-out logic with optional ML-based adjustments.
    """

    def __init__(
        self,
        credit_name: str,
        base_amount: float,
        phaseout_start: Optional[float] = None,
        phaseout_end: Optional[float] = None,
        rule_weights: Optional[Dict[str, float]] = None,
        ml_model: Optional[Any] = None,
    ):
        self.credit_name = credit_name
        self.base_amount = base_amount
        self.phaseout_start = phaseout_start
        self.phaseout_end = phaseout_end
        self.rule_weights = rule_weights or {}
        self.ml_model = ml_model

    def _compute_eligibility_probability(self, features: Dict[str, float]) -> float:
        score = 0.0
        for key, weight in self.rule_weights.items():
            score += weight * features.get(key, 0.0)
        return max(0.0, min(1.0, score))

    def _apply_phaseout(self, income: float) -> float:
        if self.phaseout_start is None or self.phaseout_end is None:
            return 1.0
        if income <= self.phaseout_start:
            return 1.0
        if income >= self.phaseout_end:
            return 0.0
        return 1.0 - ((income - self.phaseout_start) / (self.phaseout_end - self.phaseout_start))

    def _rule_based_value(self, features: Dict[str, float]) -> float:
        income = features.get("income", 0.0)
        eligibility_prob = self._compute_eligibility_probability(features)
        phaseout_factor = self._apply_phaseout(income)
        return self.base_amount * eligibility_prob * phaseout_factor

    def _ml_adjustment(self, features: Dict[str, float]) -> float:
        if self.ml_model is None:
            return 0.0
        df = pd.DataFrame([features])
        return float(self.ml_model.predict(df)[0])

    def predict(self, features: Dict[str, float]) -> CreditValuePrediction:
        rule_value = self._rule_based_value(features)
        eligibility_prob = self._compute_eligibility_probability(features)
        ml_adj = self._ml_adjustment(features)

        estimated_value = max(0.0, rule_value + ml_adj)

        return CreditValuePrediction(
            estimated_value=float(estimated_value),
            eligibility_probability=float(eligibility_prob),
            rule_based_value=float(rule_value),
            ml_adjustment=float(ml_adj),
            metadata={
                "credit_name": self.credit_name,
                "base_amount": self.base_amount,
                "phaseout_start": self.phaseout_start,
                "phaseout_end": self.phaseout_end,
                "input_features": features,
            },
        )

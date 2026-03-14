import pandas as pd
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class DeductionProbability:
    probability: float
    rule_based_score: float
    ml_adjustment: float
    metadata: Dict[str, Any]


class DeductionProbabilityModel:
    """
    Predicts the probability that a specific tax deduction applies to a user.
    Combines rule-based eligibility signals with optional ML-based scoring.
    """

    def __init__(
        self,
        deduction_name: str,
        rule_weights: Optional[Dict[str, float]] = None,
        ml_model: Optional[Any] = None,
    ):
        self.deduction_name = deduction_name
        self.rule_weights = rule_weights or {}
        self.ml_model = ml_model

    def _compute_rule_score(self, features: Dict[str, float]) -> float:
        score = 0.0
        for key, weight in self.rule_weights.items():
            value = features.get(key, 0.0)
            score += weight * value
        return max(0.0, min(1.0, score))

    def _ml_adjustment(self, features: Dict[str, float]) -> float:
        if self.ml_model is None:
            return 0.0
        df = pd.DataFrame([features])
        return float(self.ml_model.predict_proba(df)[0][1])

    def predict(self, features: Dict[str, float]) -> DeductionProbability:
        rule_score = self._compute_rule_score(features)
        ml_adj = self._ml_adjustment(features)

        final_prob = max(0.0, min(1.0, 0.6 * rule_score + 0.4 * ml_adj))

        return DeductionProbability(
            probability=float(final_prob),
            rule_based_score=float(rule_score),
            ml_adjustment=float(ml_adj),
            metadata={
                "deduction_name": self.deduction_name,
                "input_features": features,
            },
        )

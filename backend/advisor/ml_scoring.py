from decimal import Decimal
from typing import Dict, Any

from constants import ML_CONFIDENCE_FLOOR
from exceptions import ModelUnavailableError


class MLScoringEngine:
    def __init__(self, model=None, model_version=None):
        self.model = model
        self.model_version = model_version

    def score(self, features: Dict[str, Any]) -> Decimal:
        if self.model is None:
            raise ModelUnavailableError("ML model not loaded")

        raw_score = self.model.predict(features)

        score = Decimal(str(raw_score))
        return max(score, ML_CONFIDENCE_FLOOR)

    def explain_features(self, features: Dict[str, Any]) -> Dict[str, float]:
        if not hasattr(self.model, "feature_importances"):
            return {}

        return dict(self.model.feature_importances(features))

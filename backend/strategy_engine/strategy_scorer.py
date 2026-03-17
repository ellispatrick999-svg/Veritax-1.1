# strategy_scorer.py

from typing import Dict, Any, List


class StrategyScorer:
    """
    Assigns a score to each strategy based on:
    - estimated tax savings
    - risk
    - complexity
    - time sensitivity
    - confidence
    - user preferences
    """

    def __init__(self, weights: Dict[str, float] = None):
        # Default scoring weights
        self.weights = weights or {
            "tax_savings": 0.50,
            "risk": -0.20,          # negative weight: higher risk lowers score
            "complexity": -0.10,    # negative weight: more complexity lowers score
            "time_sensitivity": 0.10,
            "confidence": 0.20
        }

    def score(self, strategy_name: str, result: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """
        result = {
            "output": {...},
            "metadata": {
                "estimated_tax_savings": float,
                "risk_level": float (0-1),
                "complexity": float (0-1),
                "time_sensitivity": float (0-1),
                "confidence": float (0-1)
            }
        }
        """

        meta = result.get("metadata", {})

        # Extract metadata with safe defaults
        tax_savings = meta.get("estimated_tax_savings", 0)
        risk = meta.get("risk_level", 0.5)
        complexity = meta.get("complexity", 0.5)
        time_sensitivity = meta.get("time_sensitivity", 0.5)
        confidence = meta.get("confidence", 0.5)

        # Normalize tax savings to a 0–1 scale (you can replace this with a smarter model)
        normalized_savings = self._normalize_tax_savings(tax_savings, user)

        # Weighted score
        score = (
            normalized_savings * self.weights["tax_savings"] +
            risk * self.weights["risk"] +
            complexity * self.weights["complexity"] +
            time_sensitivity * self.weights["time_sensitivity"] +
            confidence * self.weights["confidence"]
        )

        return {
            "strategy": strategy_name,
            "score": round(score, 4),
            "components": {
                "normalized_tax_savings": normalized_savings,
                "risk": risk,
                "complexity": complexity,
                "time_sensitivity": time_sensitivity,
                "confidence": confidence
            }
        }

    def _normalize_tax_savings(self, savings: float, user: Dict[str, Any]) -> float:
        """
        Converts raw tax savings into a 0–1 scale.
        You can replace this with a more sophisticated model later.
        """
        income = user.get("net_income", 100000)
        max_reasonable_savings = max(1000, income * 0.10)  # assume 10% of income is a high-end savings

        normalized = min(savings / max_reasonable_savings, 1.0)
        return max(normalized, 0.0)

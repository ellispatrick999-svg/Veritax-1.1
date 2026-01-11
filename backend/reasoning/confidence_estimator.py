"""
confidence_estimator.py

Combines multiple signals (intent, reasoning, fact-checking, model scores)
into a single confidence value for responses.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ConfidenceInputs:
    """
    Input signals for estimating confidence.

    All fields are optional; missing values are simply ignored in aggregation.
    """
    intent_confidence: Optional[float] = None
    reasoning_confidence: Optional[float] = None
    fact_check_confidence: Optional[float] = None
    retrieval_confidence: Optional[float] = None


class ConfidenceEstimator:
    """
    Simple weighted aggregator for confidence signals.

    You can:
    - Change weights
    - Swap out aggregation strategy
    - Add calibration based on feedback
    """

    def __init__(
        self,
        w_intent: float = 0.25,
        w_reasoning: float = 0.25,
        w_fact_check: float = 0.3,
        w_retrieval: float = 0.2,
    ) -> None:
        self.w_intent = w_intent
        self.w_reasoning = w_reasoning
        self.w_fact_check = w_fact_check
        self.w_retrieval = w_retrieval

    def estimate(self, inputs: ConfidenceInputs) -> float:
        """
        Compute a final confidence value in [0.0, 1.0].

        Only non-None signals are used; weights are renormalized accordingly.
        """
        weighted_sum = 0.0
        total_weight = 0.0

        if inputs.intent_confidence is not None:
            weighted_sum += inputs.intent_confidence * self.w_intent
            total_weight += self.w_intent

        if inputs.reasoning_confidence is not None:
            weighted_sum += inputs.reasoning_confidence * self.w_reasoning
            total_weight += self.w_reasoning

        if inputs.fact_check_confidence is not None:
            weighted_sum += inputs.fact_check_confidence * self.w_fact_check
            total_weight += self.w_fact_check

        if inputs.retrieval_confidence is not None:
            weighted_sum += inputs.retrieval_confidence * self.w_retrieval
            total_weight += self.w_retrieval

        if total_weight == 0.0:
            # No signals; default conservative confidence.
            return 0.0

        return max(0.0, min(1.0, weighted_sum / total_weight))

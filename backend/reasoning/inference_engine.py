"""
Inference Engine for Ambiguous Financial Situations

Purpose:
- Resolve ambiguity WITHOUT guessing
- Generate ranked interpretations (hypotheses)
- Propagate uncertainty forward
- Decide when clarification or human review is required

Rules:
- No math that affects tax amounts
- No invention of entities
- Conservative defaults
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple


# -----------------------------
# Core enums & data models
# -----------------------------

class AmbiguityType(str, Enum):
    AMOUNT_RANGE = "amount_range"
    TIME_PERIOD = "time_period"
    CATEGORY = "category"
    MISSING_CONTEXT = "missing_context"


class Decision(str, Enum):
    ACCEPT = "accept"
    REQUEST_CLARIFICATION = "request_clarification"
    ESCALATE = "escalate"


@dataclass
class Ambiguity:
    kind: AmbiguityType
    description: str
    confidence_penalty: float  # how much certainty is reduced


@dataclass
class Hypothesis:
    """
    One plausible interpretation of the user's situation.
    """
    facts: Dict[str, Dict[str, float]]
    assumptions: List[str]
    confidence: float
    ambiguities: List[Ambiguity]


@dataclass
class InferenceResult:
    hypotheses: List[Hypothesis]
    decision: Decision
    questions_for_user: List[str]


# -----------------------------
# Heuristic thresholds
# -----------------------------

MIN_ACCEPTABLE_CONFIDENCE = 0.65
ESCALATION_CONFIDENCE = 0.4


# -----------------------------
# Inference helpers
# -----------------------------

def _apply_confidence_penalties(
    base_confidence: float,
    ambiguities: List[Ambiguity],
) -> float:
    confidence = base_confidence
    for amb in ambiguities:
        confidence *= (1.0 - amb.confidence_penalty)
    return max(min(confidence, 1.0), 0.0)


def _detect_amount_range(value: Optional[float], estimated: bool) -> List[Ambiguity]:
    ambiguities = []
    if value is None:
        ambiguities.append(
            Ambiguity(
                kind=AmbiguityType.MISSING_CONTEXT,
                description="No amount provided.",
                confidence_penalty=0.3,
            )
        )
    elif estimated:
        ambiguities.append(
            Ambiguity(
                kind=AmbiguityType.AMOUNT_RANGE,
                description="Amount appears to be an estimate.",
                confidence_penalty=0.15,
            )
        )
    return ambiguities


# -----------------------------
# Public inference API
# -----------------------------

def infer_from_facts(
    facts: Dict[str, Dict[str, float]],
    *,
    estimated_values: bool = False,
    base_confidence: float = 0.9,
) -> InferenceResult:
    """
    Main inference entry point.

    facts example:
    {
        "income": 85000,
        "deductions": {"student_loan_interest": 4000}
    }
    """

    hypotheses: List[Hypothesis] = []
    questions: List[str] = []

    # -------------------------
    # Hypothesis 1: As-stated
    # -------------------------
    ambiguities: List[Ambiguity] = []

    ambiguities.extend(
        _detect_amount_range(
            facts.get("income"),
            estimated_values,
        )
    )

    for _, amount in facts.get("deductions", {}).items():
        ambiguities.extend(
            _detect_amount_range(
                amount,
                estimated_values,
            )
        )

    confidence = _apply_confidence_penalties(
        base_confidence,
        ambiguities,
    )

    hypotheses.append(
        Hypothesis(
            facts=facts,
            assumptions=["Values are interpreted as stated."],
            confidence=confidence,
            ambiguities=ambiguities,
        )
    )

    # -------------------------
    # Hypothesis 2: Conservative
    # -------------------------
    if estimated_values:
        conservative_ambiguities = ambiguities + [
            Ambiguity(
                kind=AmbiguityType.AMOUNT_RANGE,
                description="Using conservative interpretation of estimates.",
                confidence_penalty=0.1,
            )
        ]

        conservative_confidence = _apply_confidence_penalties(
            base_confidence,
            conservative_ambiguities,
        )

        hypotheses.append(
            Hypothesis(
                facts=facts,
                assumptions=[
                    "Estimated values may be overstated.",
                    "Conservative interpretation applied.",
                ],
                confidence=conservative_confidence,
                ambiguities=conservative_ambiguities,
            )
        )

    # -------------------------
    # Sort hypotheses
    # -------------------------
    hypotheses.sort(key=lambda h: h.confidence, reverse=True)

    best = hypotheses[0]

    # -------------------------
    # Decision logic
    # -------------------------
    if best.confidence >= MIN_ACCEPTABLE_CONFIDENCE:
        decision = Decision.ACCEPT

    elif best.confidence >= ESCALATION_CONFIDENCE:
        decision = Decision.REQUEST_CLARIFICATION
        questions.extend(
            [
                "Are the amounts you provided exact or estimates?",
                "Can you confirm the time period (tax year) these amounts apply to?",
            ]
        )

    else:
        decision = Decision.ESCALATE
        questions.append(
            "This situation may require review by a licensed tax professional."
        )

    return InferenceResult(
        hypotheses=hypotheses,
        decision=decision,
        questions_for_user=questions,
    )


# -----------------------------
# Explanation helper
# -----------------------------

def summarize_inference(result: InferenceResult) -> str:
    """
    Human-readable summary for UI or reasoning layer.
    """
    lines = [
        f"Inference decision: {result.decision.value}",
        f"Number of interpretations considered: {len(result.hypotheses)}",
        "",
        "Top interpretation:",
    ]

    top = result.hypotheses[0]
    lines.append(f"Confidence: {top.confidence:.2f}")

    if top.ambiguities:
        lines.append("Remaining ambiguities:")
        for amb in top.ambiguities:
            lines.append(f" - {amb.description}")

    if result.questions_for_user:
        lines.append("")
        lines.append("Next steps:")
        for q in result.questions_for_user:
            lines.append(f" • {q}")

    return "\n".join(lines)




"""
AI Reasoning Layer

Purpose:
- Convert structured tax facts + rule outputs into
  clear, cautious, explainable guidance.
- NEVER compute tax amounts.
- NEVER invent rules.
- ALWAYS surface uncertainty and risk.

This file is the intelligence boundary.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


# -----------------------------
# Core reasoning primitives
# -----------------------------

class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ReasoningInput:
    """
    Canonical input to the reasoning layer.
    Everything here must be produced by deterministic code.
    """
    income: float
    deductions: Dict[str, float]
    estimated_tax: float
    estimated_savings: float
    audit_risk: float
    rule_sources: List[str]  # IRS publications, sections, etc.


@dataclass
class ReasoningOutput:
    """
    Canonical output from the reasoning layer.
    """
    summary: str
    explanation: str
    confidence: ConfidenceLevel
    requires_human_review: bool
    citations: List[str]


# -----------------------------
# Internal heuristics
# -----------------------------

def _confidence_from_risk(risk: float) -> ConfidenceLevel:
    if risk < 0.25:
        return ConfidenceLevel.HIGH
    if risk < 0.6:
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.LOW


def _needs_human_review(risk: float, savings: float) -> bool:
    """
    Escalate if risk is high or money impact is large.
    """
    if risk >= 0.7:
        return True
    if savings >= 5000:
        return True
    return False


# -----------------------------
# Public reasoning API
# -----------------------------

def reason_about_tax_position(
    data: ReasoningInput,
) -> ReasoningOutput:
    """
    Produce a safe, explainable interpretation
    of the user's tax position.
    """

    confidence = _confidence_from_risk(data.audit_risk)
    escalation = _needs_human_review(
        data.audit_risk,
        data.estimated_savings,
    )

    summary = (
        f"Your estimated tax is ${data.estimated_tax:,.0f}, "
        f"with potential savings of ${data.estimated_savings:,.0f}."
    )

    explanation_lines = [
        f"• Total reported income: ${data.income:,.0f}",
        "• Deductions considered:",
    ]

    for name, amount in data.deductions.items():
        explanation_lines.append(f"  - {name}: ${amount:,.0f}")

    explanation_lines.extend(
        [
            "",
            f"Audit risk assessment: {data.audit_risk:.2f}",
            f"Confidence level: {confidence.value}",
        ]
    )

    if escalation:
        explanation_lines.append(
            ""
        )
        explanation_lines.append(
            "⚠️ This situation may benefit from review by a licensed tax professional."
        )

    explanation = "\n".join(explanation_lines)

    return ReasoningOutput(
        summary=summary,
        explanation=explanation,
        confidence=confidence,
        requires_human_review=escalation,
        citations=data.rule_sources,
    )


# -----------------------------
# Optional LLM enhancement hook
# -----------------------------

def llm_friendly_explanation(
    reasoning: ReasoningOutput,
) -> str:
    """
    This function is safe to pass to an LLM.
    It contains NO numbers that affect computation.
    """

    base = reasoning.explanation

    if reasoning.confidence == ConfidenceLevel.LOW:
        base += (
            "\n\nThis explanation is provided for understanding only "
            "and should not be relied upon without professional review."
        )

    return base

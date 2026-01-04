"""
Tax Rule Router

Purpose:
- Decide which tax rules MAY apply to a user’s situation
- NEVER calculate tax
- NEVER decide eligibility conclusively
- ALWAYS explain inclusion/exclusion logic

This module answers:
"Which rules should we even look at?"
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


# -----------------------------
# Core data models
# -----------------------------

class FilingStatus(str, Enum):
    SINGLE = "single"
    MARRIED_JOINT = "married_filing_jointly"
    MARRIED_SEPARATE = "married_filing_separately"
    HEAD_OF_HOUSEHOLD = "head_of_household"


@dataclass
class TaxContext:
    """
    Canonical context for rule routing.
    All values must be factual or explicitly inferred upstream.
    """
    tax_year: int
    filing_status: FilingStatus
    income: Optional[float]
    deductions: Dict[str, float]
    dependents: int = 0
    has_student_loans: bool = False
    has_mortgage: bool = False
    has_self_employment_income: bool = False


@dataclass
class RuleMatch:
    rule_id: str
    description: str
    reason_applied: str
    confidence: float
    requires_additional_validation: bool


@dataclass
class RuleRoutingResult:
    applicable_rules: List[RuleMatch]
    excluded_rules: Dict[str, str]  # rule_id → exclusion reason


# -----------------------------
# Rule registry (declarative)
# -----------------------------

RULE_REGISTRY = {
    "STD_DEDUCTION": {
        "description": "Standard Deduction",
        "conditions": lambda ctx: True,
        "confidence": 0.95,
    },
    "STUDENT_LOAN_INTEREST": {
        "description": "Student Loan Interest Deduction",
        "conditions": lambda ctx: ctx.has_student_loans,
        "confidence": 0.75,
    },
    "MORTGAGE_INTEREST": {
        "description": "Mortgage Interest Deduction",
        "conditions": lambda ctx: ctx.has_mortgage,
        "confidence": 0.8,
    },
    "SELF_EMPLOYMENT_TAX": {
        "description": "Self-Employment Tax Rules",
        "conditions": lambda ctx: ctx.has_self_employment_income,
        "confidence": 0.9,
    },
    "CHILD_TAX_CREDIT": {
        "description": "Child Tax Credit",
        "conditions": lambda ctx: ctx.dependents > 0,
        "confidence": 0.85,
    },
}


# -----------------------------
# Public routing API
# -----------------------------

def route_tax_rules(context: TaxContext) -> RuleRoutingResult:
    """
    Determines which tax rules may apply
    based on the provided tax context.
    """

    applicable: List[RuleMatch] = []
    excluded: Dict[str, str] = {}

    for rule_id, rule in RULE_REGISTRY.items():
        try:
            applies = rule["conditions"](context)
        except Exception as e:
            excluded[rule_id] = f"Condition evaluation failed: {e}"
            continue

        if applies:
            applicable.append(
                RuleMatch(
                    rule_id=rule_id,
                    description=rule["description"],
                    reason_applied=_explain_reason(rule_id, context),
                    confidence=rule["confidence"],
                    requires_additional_validation=True,
                )
            )
        else:
            excluded[rule_id] = _explain_exclusion(rule_id, context)

    return RuleRoutingResult(
        applicable_rules=applicable,
        excluded_rules=excluded,
    )


# -----------------------------
# Explanation helpers
# -----------------------------

def _explain_reason(rule_id: str, ctx: TaxContext) -> str:
    if rule_id == "STUDENT_LOAN_INTEREST":
        return "User indicated presence of student loan payments."
    if rule_id == "MORTGAGE_INTEREST":
        return "User indicated a mortgage exists."
    if rule_id == "SELF_EMPLOYMENT_TAX":
        return "User has self-employment income."
    if rule_id == "CHILD_TAX_CREDIT":
        return f"User reported {ctx.dependents} dependents."
    if rule_id == "STD_DEDUCTION":
        return "Standard deduction is universally available."
    return "Conditions satisfied."


def _explain_exclusion(rule_id: str, ctx: TaxContext) -> str:
    if rule_id == "STUDENT_LOAN_INTEREST":
        return "No student loan activity indicated."
    if rule_id == "MORTGAGE_INTEREST":
        return "No mortgage indicated."
    if rule_id == "SELF_EMPLOYMENT_TAX":
        return "No self-employment income indicated."
    if rule_id == "CHILD_TAX_CREDIT":
        return "No dependents reported."
    return "Conditions not met."


# -----------------------------
# Summary helper (UI / reasoning)
# -----------------------------

def summarize_rule_routing(result: RuleRoutingResult) -> str:
    lines = [
        "Applicable tax rules identified:",
    ]

    for rule in result.applicable_rules:
        lines.append(
            f" • {rule.rule_id}: {rule.description} "
            f"(confidence: {rule.confidence:.2f})"
        )

    if result.excluded_rules:
        lines.append("")
        lines.append("Rules not applied:")
        for rule_id, reason in result.excluded_rules.items():
            lines.append(f" • {rule_id}: {reason}")

    return "\n".join(lines)

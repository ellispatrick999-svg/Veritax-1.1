"""
Context Builder for Tax AI

Purpose:
- Convert messy, ambiguous, or partial input into structured TaxContext
- Integrates NLP-parsed entities + user metadata + estimates
- Adds explicit flags for uncertainty
- Ready for downstream inference, rule routing, and reasoning
"""

from dataclasses import dataclass, field
from typing import Dict, Optional

from backend.tax_engine.rule_router import FilingStatus, TaxContext


@dataclass
class ContextBuildResult:
    """
    Result of building a tax context.
    """
    context: TaxContext
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


# -----------------------------
# Core builder
# -----------------------------

def build_tax_context(
    *,
    income: Optional[float] = None,
    deductions: Optional[Dict[str, float]] = None,
    filing_status: Optional[str] = None,
    dependents: Optional[int] = None,
    estimated_flags: Optional[Dict[str, bool]] = None,
    tax_year: int = 2025,
) -> ContextBuildResult:
    """
    Build a canonical TaxContext from messy input.
    Adds warnings and notes for missing or estimated values.

    Parameters:
    - income: user-reported or parsed income
    - deductions: dict of deduction name -> value
    - filing_status: user input, mapped to FilingStatus
    - dependents: number of dependents
    - estimated_flags: dict like {"income": True, "mortgage": False}
    - tax_year: integer tax year
    """

    warnings = []
    notes = []
    deductions = deductions or {}
    estimated_flags = estimated_flags or {}

    # -------------------------
    # Filing status normalization
    # -------------------------
    status_map = {
        "single": FilingStatus.SINGLE,
        "s": FilingStatus.SINGLE,
        "married_joint": FilingStatus.MARRIED_JOINT,
        "married_separate": FilingStatus.MARRIED_SEPARATE,
        "head_of_household": FilingStatus.HEAD_OF_HOUSEHOLD,
        "hoh": FilingStatus.HEAD_OF_HOUSEHOLD,
    }

    if filing_status is None:
        normalized_status = FilingStatus.SINGLE
        warnings.append("Filing status missing, defaulting to SINGLE.")
    else:
        normalized_status = status_map.get(filing_status.lower())
        if normalized_status is None:
            normalized_status = FilingStatus.SINGLE
            warnings.append(f"Unrecognized filing status '{filing_status}', defaulting to SINGLE.")

    # -------------------------
    # Income
    # -------------------------
    if income is None:
        warnings.append("Income missing; some rules may not apply accurately.")
        income_value = 0.0
    else:
        income_value = float(income)
        if estimated_flags.get("income"):
            notes.append("Income marked as estimated; confidence reduced.")

    # -------------------------
    # Deductions and flags
    # -------------------------
    has_student_loans = "student_loan_interest" in deductions
    if estimated_flags.get("student_loan_interest"):
        notes.append("Student loan deduction is estimated.")

    has_mortgage = "mortgage_interest" in deductions
    if estimated_flags.get("mortgage_interest"):
        notes.append("Mortgage deduction is estimated.")

    has_self_employment_income = estimated_flags.get("self_employment", False)

    dependents_value = dependents if dependents is not None else 0

    context = TaxContext(
        tax_year=tax_year,
        filing_status=normalized_status,
        income=income_value,
        deductions=deductions,
        dependents=dependents_value,
        has_student_loans=has_student_loans,
        has_mortgage=has_mortgage,
        has_self_employment_income=has_self_employment_income,
    )

    return ContextBuildResult(
        context=context,
        warnings=warnings,
        notes=notes,
    )


# -----------------------------
# Helper for UI / logging
# -----------------------------

def summarize_context(result: ContextBuildResult) -> str:
    lines = [
        f"TaxContext for year {result.context.tax_year}:",
        f" • Filing status: {result.context.filing_status.value}",
        f" • Income: ${result.context.income:,.0f}",
        f" • Deductions: {result.context.deductions}",
        f" • Dependents: {result.context.dependents}",

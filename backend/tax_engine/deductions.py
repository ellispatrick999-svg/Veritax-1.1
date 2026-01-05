"""
deductions.py

Handles standard and itemized deduction calculations with validation.
"""

from dataclasses import dataclass
from typing import Dict, Optional


# -----------------------------
# Standard Deduction Rules
# -----------------------------

STANDARD_DEDUCTIONS = {
    "single": 13850,
    "married_joint": 27700,
    "married_separate": 13850,
    "head_of_household": 20800,
}


def get_standard_deduction(filing_status: str) -> float:
    """
    Return the standard deduction based on filing status.

    :param filing_status: Filing status string
    :return: Standard deduction amount
    """
    filing_status = filing_status.lower()

    if filing_status not in STANDARD_DEDUCTIONS:
        raise ValueError(f"Invalid filing status: {filing_status}")

    return STANDARD_DEDUCTIONS[filing_status]


# -----------------------------
# Itemized Deductions
# -----------------------------

@dataclass
class ItemizedDeductions:
    """
    Represents itemized deductions.
    """
    medical_expenses: float = 0.0
    state_local_taxes: float = 0.0  # SALT
    mortgage_interest: float = 0.0
    charitable_contributions: float = 0.0
    casualty_losses: float = 0.0


SALT_CAP = 10_000  # SALT deduction cap


def calculate_itemized_deductions(
    deductions: ItemizedDeductions,
    adjusted_gross_income: float
) -> float:
    """
    Calculate total itemized deductions after applying limits.

    :param deductions: ItemizedDeductions object
    :param adjusted_gross_income: AGI for medical expense threshold
    :return: Total itemized deductions
    """
    if adjusted_gross_income < 0:
        raise ValueError("Adjusted gross income cannot be negative")

    # Medical expenses: only amount above 7.5% of AGI
    medical_threshold = 0.075 * adjusted_gross_income
    allowable_medical = max(0.0, deductions.medical_expenses - medical_threshold)

    # SALT deduction capped
    allowable_salt = min(deductions.state_local_taxes, SALT_CAP)

    total = (
        allowable_medical
        + allowable_salt
        + max(0.0, deductions.mortgage_interest)
        + max(0.0, deductions.charitable_contributions)
        + max(0.0, deductions.casualty_losses)
    )

    return round(total, 2)


# -----------------------------
# Best Deduction Choice
# -----------------------------

def calculate_best_deduction(
    filing_status: str,
    adjusted_gross_income: float,
    itemized: Optional[ItemizedDeductions] = None
) -> Dict[str, float]:
    """
    Determine whether standard or itemized deduction is better.

    :param filing_status: Filing status
    :param adjusted_gross_income: AGI
    :param itemized: Optional itemized deductions
    :return: Dict with deduction type and amount

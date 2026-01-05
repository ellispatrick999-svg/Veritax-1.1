"""
filing_taxes.py

Main tax filing logic that:
- Validates filing status
- Applies deductions
- Calculates taxable income
- Applies progressive tax brackets
- Applies credits
"""

from typing import Dict, Optional

from brackets import calculate_progressive_tax, DEFAULT_BRACKETS
from deductions import (
    get_standard_deduction,
    calculate_itemized_deductions,
    ItemizedDeductions,
)
from credits import calculate_total_credits


# -----------------------------
# Filing Status Rules
# -----------------------------

VALID_FILING_STATUSES = {
    "single",
    "married_joint",
    "married_separate",
    "head_of_household",
}


def validate_filing_status(status: str) -> str:
    status = status.lower()
    if status not in VALID_FILING_STATUSES:
        raise ValueError(f"Invalid filing status: {status}")
    return status


# -----------------------------
# Core Tax Filing Function
# -----------------------------

def file_taxes(
    *,
    filing_status: str,
    gross_income: float,
    earned_income: float,
    qualifying_children: int = 0,
    itemized_deductions: Optional[ItemizedDeductions] = None,
    tax_brackets=DEFAULT_BRACKETS,
) -> Dict[str, float]:
    """
    File taxes and return a full tax summary.

    :return: Dict containing tax breakdown
    """
    filing_status = validate_filing_status(filing_status)

    if gross_income < 0 or earned_income < 0:
        raise ValueError("Income values cannot be negative")

    # -----------------------------
    # Adjusted Gross Income (AGI)
    # -----------------------------
    agi = gross_income  # placeholder for future adjustments

    # -----------------------------
    # Deductions
    # -----------------------------
    standard_deduction = get_standard_deduction(filing_status)

    if itemized_deductions:
        itemized_total = calculate_itemized_deductions(
            itemized_deductions, agi
        )
        deduction_used = max(standard_deduction, itemized_total)
        deduction_type = (
            "itemized" if itemized_total > standard_deduction else "standard"
        )
    else:
        deduction_used = standard_deduction
        deduction_type = "standard"

    # -----------------------------
    # Taxable Income
    # -----------------------------
    taxable_income = max(0.0, agi - deduction_used)

    # -----------------------------
    # Base Tax
    # -----------------------------
    base_tax = calculate_progressive_tax(
        taxable_income, tax_brackets
    )

    # -----------------------------
    # Credits
    # -----------------------------
    credits = calculate_total_credits(
        filing_status=filing_status,
        ag

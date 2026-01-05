"""
credits.py

Handles common tax credits such as:
- Child Tax Credit (CTC)
- Earned Income Tax Credit (EITC)

Designed to be configurable and easy to update as rules change.
"""

from dataclasses import dataclass
from typing import Dict


# -----------------------------
# Child Tax Credit (CTC)
# -----------------------------

CTC_PER_CHILD = 2000
CTC_REFUNDABLE_LIMIT = 1600

CTC_PHASEOUT_THRESHOLDS = {
    "single": 200_000,
    "head_of_household": 200_000,
    "married_joint": 400_000,
    "married_separate": 200_000,
}

CTC_PHASEOUT_RATE = 0.05  # $50 per $1,000 over threshold


def calculate_child_tax_credit(
    filing_status: str,
    agi: float,
    qualifying_children: int,
) -> Dict[str, float]:
    """
    Calculate the Child Tax Credit.

    :return: Dict with total, refundable, and nonrefundable portions
    """
    if qualifying_children <= 0:
        return {"total": 0.0, "refundable": 0.0, "nonrefundable": 0.0}

    max_credit = qualifying_children * CTC_PER_CHILD
    threshold = CTC_PHASEOUT_THRESHOLDS.get(filing_status)

    if threshold is None:
        raise ValueError(f"Invalid filing status: {filing_status}")

    # Phaseout calculation
    if agi > threshold:
        excess = agi - threshold
        reduction = (excess // 1000) * (CTC_PHASEOUT_RATE * 1000)
        max_credit = max(0.0, max_credit - reduction)

    refundable = min(max_credit, qualifying_children * CTC_REFUNDABLE_LIMIT)
    nonrefundable = max_credit - refundable

    return {
        "total": round(max_credit, 2),
        "refundable": round(refundable, 2),
        "nonrefundable": round(nonrefundable, 2),
    }


# -----------------------------
# Earned Income Tax Credit (EITC)
# -----------------------------

@dataclass
class EITCRule:
    max_credit: float
    phase_in_rate: float
    phase_out_rate: float
    phase_out_start: float


EITC_RULES = {
    0: EITCRule(600, 0.0765, 0.0765, 9_800),
    1: EITCRule(3995, 0.34, 0.1598, 21_560),
    2: EITCRule(6604, 0.40, 0.2106, 21_560),
    3: EITCRule(7430, 0.45, 0.2106, 21_560),
}


def calculate_eitc(
    earned_income: float,
    agi: float,
    qualifying_children: int,
) -> float:
    """
    Calculate Earned Income Tax Credit (simplified).

    :return: EITC amount
    """
    children = min(qualifying_children, 3)
    rule = EITC_RULES[children]

    income = min(earned_income, agi)

    # Phase-in
    credit = min(rule.max_credit, income * rule.phase_in_rate)

    # Phase-out
    if income > rule.phase_out_start:
        reduction = (income - rule.phase_out_start) * rule.phase_out_rate
        credit = max(0.0, credit - reduction)

    return round(credit, 2)


# -----------------------------
# Total Credits Wrapper
# -----------------------------

def calculate_total_credits(
    filing_status: str,
    agi: float,
    earned_income: float,
    qualifying_children: int,
) -> Dict[str, float]:
    """
    Calculate all supported tax credits.

    :return: Dict with breakdown and total
    """
    ctc = calculate_child_tax_credit(
        filing_status=filing_status,
        agi=agi,
        qualifying_children=qualifying_children,
    )

    eitc = calculate_eitc(
        earned_income=earned_income,
        agi=agi,
        qualifying_children=qualifying_children,
    )

    total = ctc["total"] + eitc

    return {
        "child_tax_credit": ctc,
        "earned_income_tax_credit": eitc,
        "total_credits": round(total, 2),
    }


# -----------------------------
# Example Usage
# -----------------------------

if __name__ == "__main__":
    result = calculate_total_credits(
        filing_status="single",
        agi=42_000,
        earned_income=40_000,
        qualifying_children=1,
    )

    for k, v in result.items():
        print(f"{k}: {v}")

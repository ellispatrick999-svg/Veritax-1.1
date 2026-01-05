"""
business_rules.py

Advanced business tax rules:
- Multiple Schedule C businesses
- 1099 income handling
- Business expenses
- Net profit aggregation
- Self-employment tax
- Above-the-line SE tax deduction
- Qualified Business Income (QBI) deduction (simplified)
"""

from dataclasses import dataclass
from typing import Dict, List


# -----------------------------
# Constants
# -----------------------------

SE_TAX_RATE = 0.153
SE_TAX_DEDUCTION_RATE = 0.5
SOCIAL_SECURITY_WAGE_BASE = 168_600

QBI_DEDUCTION_RATE = 0.20
QBI_INCOME_LIMITS = {
    "single": 191_950,
    "head_of_household": 191_950,
    "married_joint": 383_900,
    "married_separate": 191_950,
}


# -----------------------------
# Business Expenses
# -----------------------------

@dataclass
class BusinessExpenses:
    advertising: float = 0.0
    office_expenses: float = 0.0
    supplies: float = 0.0
    meals: float = 0.0
    travel: float = 0.0
    vehicle: float = 0.0
    home_office: float = 0.0
    insurance: float = 0.0
    professional_fees: float = 0.0
    depreciation: float = 0.0
    other: float = 0.0

    def total(self) -> float:
        return round(
            sum(max(0.0, v) for v in self.__dict__.values()),
            2,
        )


# -----------------------------
# Schedule C
# -----------------------------

@dataclass
class ScheduleC:
    business_name: str
    gross_receipts: float
    expenses: BusinessExpenses

    def net_profit(self) -> float:
        return round(self.gross_receipts - self.expenses.total(), 2)


def calculate_schedule_c(schedule: ScheduleC) -> Dict[str, float]:
    if schedule.gross_receipts < 0:
        raise ValueError("Gross receipts cannot be negative")

    return {
        "business_name": schedule.business_name,
        "gross_receipts": round(schedule.gross_receipts, 2),
        "total_expenses": schedule.expenses.total(),
        "net_profit": schedule.net_profit(),
    }


# -----------------------------
# Multiple Businesses
# -----------------------------

def aggregate_business_income(
    schedules: List[ScheduleC],
) -> Dict[str, float]:
    results = [calculate_schedule_c(s) for s in schedules]

    total_net_profit = round(
        sum(r["net_profit"] for r in results),
        2,
    )

    return {
        "businesses": results,
        "total_net_profit": total_net_profit,
    }


# -----------------------------
# Self-Employment Tax
# -----------------------------

def calculate_self_employment_tax(net_profit: float) -> Dict[str, float]:
    if net_profit <= 0:
        return {
            "se_tax": 0.0,
            "deductible_se_tax": 0.0,
        }

    taxable_se_income = net_profit * 0.9235

    ss_taxable = min(taxable_se_income, SOCIAL_SECURITY_WAGE_BASE)
    ss_tax = ss_taxable * 0.124
    medicare_tax = taxable_se_income * 0.029

    se_tax = round(ss_tax + medicare_tax, 2)
    deductible = round(se_tax * SE_TAX_DEDUCTION_RATE, 2)

    return {
        "se_tax": se_tax,
        "deductible_se_tax": deductible,
    }


# -----------------------------
# Qualified Business Income (QBI)
# -----------------------------

def calculate_qbi_deduction(
    filing_status: str,
    total_qbi: float,
    taxable_income_before_qbi: float,
) -> float:
    """
    Simplified QBI deduction (no SSTB phaseouts or wage limits).
    """
    if total_qbi <= 0:
        return 0.0

    income_limit = QBI_INCOME_LIMITS.get(filing_status)
    if income_limit is None:
        raise ValueError(f"Invalid filing status: {filing_status}")

    if taxable_income_before_qbi > income_limit:
        # Placeholder for complex phaseout logic
        return 0.0

    qbi_deduction = min(
        total_qbi * QBI_DEDUCTION_RATE,
        taxable_income_before_qbi * QBI_DEDUCTION_RATE,
    )

    return round(qbi_deduction, 2)


# -----------------------------
# Full Business Tax Wrapper
# -----------------------------

def calculate_business_tax_profile(
    filing_status: str,
    schedules: List[ScheduleC],
    taxable_income_before_qbi: float,
) -> Dict[str, float]:
    aggregated = aggregate_business_income(schedules)

    se_tax_info = calculate_self_employment_tax(
        aggregated["total_net_profit"]
    )

    qbi_deduction = calculate_qbi_deduction(
        filing_status=filing_status,
        total_qbi=aggregated["total_net_profit"],
        taxable_income_before_qbi=taxable_income_before_qbi,
    )

    return {
        "schedule_c": aggregated,
        "self_employment_tax": se_tax_info,
        "qbi_deduction": qbi_deduction,
    }


# -----------------------------
# Example Usage
# -----------------------------

if __name__ == "__main__":
    schedules = [
        ScheduleC(
            business_name="Design Studio",
            gross_receipts=60_000,
            expenses=BusinessExpenses(
                supplies=3000,
                advertising=2500,
                home_office=4000,
            ),
        ),
        ScheduleC(
            business_name="Consulting",
            gross_receipts=35_000,
            expenses=BusinessExpenses(
                travel=1800,
                professional_fees=2200,
            ),
        ),
    ]

    profile = calculate_business_tax_profile(
        filing_status="single",
        schedules=schedules,
        taxable_income_before_qbi=90_000,
    )

    for key, value in profile.items():
        print(key, value)


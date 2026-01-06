"""
risk_scoring.py

Deduction and behavior risk scoring engine.
Flags high-risk patterns associated with IRS audits.

This module DOES NOT provide advice.
It only evaluates risk signals.
"""

from dataclasses import dataclass
from typing import Dict, List


# =====================================================
# MODELS
# =====================================================

@dataclass
class RiskFlag:
    code: str
    description: str
    severity: int      # 1–10
    score_impact: int


@dataclass
class RiskScore:
    total_score: int
    risk_level: str
    flags: List[RiskFlag]


# =====================================================
# RISK THRESHOLDS
# =====================================================

RISK_LEVELS = {
    "LOW": 0,
    "MODERATE": 25,
    "HIGH": 50,
    "SEVERE": 75,
}


# =====================================================
# RISK RULE ENGINE
# =====================================================

class DeductionRiskEngine:
    def __init__(self):
        self.flags: List[RiskFlag] = []

    def add_flag(
        self,
        code: str,
        description: str,
        severity: int,
        score_impact: int
    ):
        self.flags.append(
            RiskFlag(
                code=code,
                description=description,
                severity=severity,
                score_impact=score_impact
            )
        )

    # -------------------------------------------------
    # SECTION 179 / DEPRECIATION
    # -------------------------------------------------

    def rule_high_section179(self, form_4562: Dict, total_income: float):
        sec179 = form_4562.get("Part I Section 179", 0)

        if total_income > 0 and sec179 / total_income > 0.50:
            self.add_flag(
                code="R179_RATIO_HIGH",
                description="Section 179 exceeds 50% of total income",
                severity=9,
                score_impact=25
            )

    def rule_bonus_heavy(self, form_4562: Dict):
        bonus = form_4562.get("Part II Bonus Depreciation", 0)

        if bonus > 0:
            self.add_flag(
                code="BONUS_USED",
                description="Bonus depreciation claimed",
                severity=5,
                score_impact=10
            )

    # -------------------------------------------------
    # SCHEDULE C RISKS
    # -------------------------------------------------

    def rule_schedule_c_loss(self, schedule_c: Dict):
        net_profit = schedule_c.get("Net Profit", 0)

        if net_profit < 0:
            self.add_flag(
                code="SC_LOSS",
                description="Schedule C net loss reported",
                severity=7,
                score_impact=18
            )

    def rule_round_number_income(self, schedule_c: Dict):
        net_profit = schedule_c.get("Net Profit", 0)

        if net_profit and net_profit % 1000 == 0:
            self.add_flag(
                code="SC_ROUND_NUM",
                description="Schedule C net profit is a round number",
                severity=4,
                score_impact=8
            )

    # -------------------------------------------------
    # DEDUCTION VS INCOME RATIOS
    # -------------------------------------------------

    def rule_deductions_exceed_income(
        self,
        total_income: float,
        deductions: float
    ):
        if total_income > 0 and deductions > total_income:
            self.add_flag(
                code="DED_GT_INCOME",
                description="Total deductions exceed total income",
                severity=10,
                score_impact=30
            )

    # -------------------------------------------------
    # BEHAVIORAL / PATTERN RISKS
    # -------------------------------------------------

    def rule_large_year_over_year_change(
        self,
        prior_year: float,
        current_year: float
    ):
        if prior_year <= 0:
            return

        if current_year / prior_year > 3:
            self.add_flag(
                code="YOY_DED_SPIKE",
                description="Large year-over-year change in deductions",
                severity=8,
                score_impact=20
            )

    # -------------------------------------------------
    # FINAL SCORING
    # -------------------------------------------------

    def score(self) -> RiskScore:
        total = min(100, sum(f.score_impact for f in self.flags))

        if total < RISK_LEVELS["MODERATE"]:
            level = "LOW"
        elif total < RISK_LEVELS["HIGH"]:
            level = "MODERATE"
        elif total < RISK_LEVELS["SEVERE"]:
            level = "HIGH"
        else:
            level = "SEVERE"

        return RiskScore(
            total_score=total,
            risk_level=level,
            flags=self.flags
        )


# =====================================================
# PUBLIC API
# =====================================================

def run_risk_scoring(
    irs_return: Dict,
    prior_year_deductions: float = 0.0
) -> RiskScore:
    """
    Entry point for deduction risk scoring.
    """

    engine = DeductionRiskEngine()

    forms = {f.get("Form"): f for f in irs_return.get("Forms", [])}

    form_1040 = forms.get("1040", {})
    form_4562 = forms.get("4562", {})
    schedule_c = forms.get("Schedule C", {})

    total_income = form_1040.get("Line 9", 0)
    deductions = form_1040.get("Line 12", 0)

    # Apply rules
    if form_4562:
        engine.rule_high_section179(form_4562, total_income)
        engine.rule_bonus_heavy(form_4562)

    if schedule_c:
        engine.rule_schedule_c_loss(schedule_c)
        engine.rule_round_number_income(schedule_c)

    engine.rule_deductions_exceed_income(total_income, deductions)

    if prior_year_deductions:
        engine.rule_large_year_over_year_change(
            prior_year_deductions,
            deductions
        )

    return engine.score()

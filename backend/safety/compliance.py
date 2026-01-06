"""
compliance.py

IRS compliance enforcement layer.
This module validates that computed returns conform
to structural IRS rules and constraints.

It does NOT compute tax.
It only validates correctness and legality of structure.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


# =====================================================
# MODELS
# =====================================================

@dataclass
class ComplianceIssue:
    code: str
    message: str
    severity: str  # INFO | WARNING | ERROR


@dataclass
class ComplianceResult:
    compliant: bool
    issues: List[ComplianceIssue]


# =====================================================
# CONSTANTS (IRS CONSTRAINTS)
# =====================================================

SECTION_179_LIMIT = 1_220_000      # soft-coded, configurable later
BONUS_MAX_RATE = 1.00              # 100%
SE_TAX_RATE = 0.153
SE_INCOME_FACTOR = 0.9235


# =====================================================
# CORE VALIDATORS
# =====================================================

def validate_required_forms(forms: List[Dict]) -> List[ComplianceIssue]:
    issues = []

    form_names = {f.get("Form") for f in forms}

    if "4562" in form_names and "Schedule C" not in form_names:
        issues.append(
            ComplianceIssue(
                code="FORM_DEP_MISSING_SC",
                message="Form 4562 present without Schedule C",
                severity="ERROR"
            )
        )

    if "Schedule SE" in form_names and "Schedule C" not in form_names:
        issues.append(
            ComplianceIssue(
                code="FORM_SE_MISSING_SC",
                message="Schedule SE requires Schedule C",
                severity="ERROR"
            )
        )

    return issues


def validate_section179(form_4562: Dict) -> List[ComplianceIssue]:
    issues = []

    sec179 = form_4562.get("Part I Section 179", 0)

    if sec179 < 0:
        issues.append(
            ComplianceIssue(
                code="179_NEGATIVE",
                message="Section 179 deduction cannot be negative",
                severity="ERROR"
            )
        )

    if sec179 > SECTION_179_LIMIT:
        issues.append(
            ComplianceIssue(
                code="179_LIMIT_EXCEEDED",
                message="Section 179 exceeds IRS annual limit",
                severity="ERROR"
            )
        )

    return issues


def validate_bonus_depreciation(form_4562: Dict) -> List[ComplianceIssue]:
    issues = []

    bonus = form_4562.get("Part II Bonus Depreciation", 0)

    if bonus < 0:
        issues.append(
            ComplianceIssue(
                code="BONUS_NEGATIVE",
                message="Bonus depreciation cannot be negative",
                severity="ERROR"
            )
        )

    return issues


def validate_schedule_c(schedule_c: Dict) -> List[ComplianceIssue]:
    issues = []

    net_profit = schedule_c.get("Net Profit", 0)

    if net_profit < 0:
        issues.append(
            ComplianceIssue(
                code="SC_NEGATIVE_PROFIT",
                message="Schedule C net loss detected (allowed, flagged)",
                severity="INFO"
            )
        )

    return issues


def validate_schedule_se(schedule_se: Dict, schedule_c: Dict) -> List[ComplianceIssue]:
    issues = []

    se_tax = schedule_se.get("Line 12", 0)
    net_profit = schedule_c.get("Net Profit", 0)

    expected_base = max(0, net_profit * SE_INCOME_FACTOR)
    expected_tax = round(expected_base * SE_TAX_RATE, 2)

    if abs(se_tax - expected_tax) > 5:
        issues.append(
            ComplianceIssue(
                code="SE_TAX_MISMATCH",
                message="Schedule SE tax does not match Schedule C income",
                severity="ERROR"
            )
        )

    return issues


def validate_1040(form_1040: Dict) -> List[ComplianceIssue]:
    issues = []

    total_income = form_1040.get("Line 9", 0)
    taxable_income = form_1040.get("Line 15", 0)

    if total_income < 0:
        issues.append(
            ComplianceIssue(
                code="1040_NEG_INCOME",
                message="Total income cannot be negative",
                severity="ERROR"
            )
        )

    if taxable_income < 0:
        issues.append(
            ComplianceIssue(
                code="1040_NEG_TAXABLE",
                message="Taxable income cannot be negative",
                severity="ERROR"
            )
        )

    if taxable_income > total_income:
        issues.append(
            ComplianceIssue(
                code="1040_INVALID_TAXABLE",
                message="Taxable income exceeds total income",
                severity="ERROR"
            )
        )

    return issues


# =====================================================
# MASTER COMPLIANCE CHECK
# =====================================================

def run_compliance_check(irs_return: Dict) -> ComplianceResult:
    issues: List[ComplianceIssue] = []

    forms = irs_return.get("Forms", [])

    # ---- Required form relationships
    issues.extend(validate_required_forms(forms))

    # ---- Index forms
    form_map = {f.get("Form"): f for f in forms}

    # ---- Form 4562
    if "4562" in form_map:
        issues.extend(validate_section179(form_map["4562"]))
        issues.extend(validate_bonus_depreciation(form_map["4562"]))

    # ---- Schedule C
    if "Schedule C" in form_map:
        issues.extend(validate_schedule_c(form_map["Schedule C"]))

    # ---- Schedule SE
    if "Schedule SE" in form_map and "Schedule C" in form_map:
        issues.extend(
            validate_schedule_se(
                form_map["Schedule SE"],
                form_map["Schedule C"]
            )
        )

    # ---- Form 1040
    if "1040" in form_map:
        issues.extend(validate_1040(form_map["1040"]))

    compliant = not any(i.severity == "ERROR" for i in issues)

    return ComplianceResult(
        compliant=compliant,
        issues=issues
    )

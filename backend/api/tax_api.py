from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum

# -----------------------------------
# App Initialization
# -----------------------------------

app = FastAPI(
    title="CPA-Level Tax Calculation API",
    version="1.0.0",
    description="Deterministic federal income tax calculations"
)

# -----------------------------------
# Enums & Constants
# -----------------------------------

class FilingStatus(str, Enum):
    SINGLE = "single"
    MARRIED_JOINT = "married_joint"
    MARRIED_SEPARATE = "married_separate"
    HEAD_OF_HOUSEHOLD = "head_of_household"

STANDARD_DEDUCTION_2024 = {
    FilingStatus.SINGLE: 14600,
    FilingStatus.MARRIED_JOINT: 29200,
    FilingStatus.MARRIED_SEPARATE: 14600,
    FilingStatus.HEAD_OF_HOUSEHOLD: 21900,
}

FEDERAL_TAX_BRACKETS_2024 = {
    FilingStatus.SINGLE: [
        (0, 0.10),
        (11600, 0.12),
        (47150, 0.22),
        (100525, 0.24),
        (191950, 0.32),
        (243725, 0.35),
        (609350, 0.37),
    ],
    FilingStatus.MARRIED_JOINT: [
        (0, 0.10),
        (23200, 0.12),
        (94300, 0.22),
        (201050, 0.24),
        (383900, 0.32),
        (487450, 0.35),
        (731200, 0.37),
    ],
}

# -----------------------------------
# Request / Response Models
# -----------------------------------

class IncomeItem(BaseModel):
    source: str
    amount: float

class DeductionItem(BaseModel):
    name: str
    amount: float

class TaxCalculationRequest(BaseModel):
    tax_year: int = 2024
    filing_status: FilingStatus
    incomes: List[IncomeItem]
    itemized_deductions: Optional[List[DeductionItem]] = None
    dependents: int = 0
    credits: float = 0.0

class TaxBracketDetail(BaseModel):
    bracket_start: float
    rate: float
    taxed_amount: float
    tax: float

class TaxCalculationResponse(BaseModel):
    gross_income: float
    adjusted_gross_income: float
    deduction_used: float
    taxable_income: float
    bracket_breakdown: List[TaxBracketDetail]
    total_tax_before_credits: float
    credits_applied: float
    total_tax_liability: float
    explanation: str

# -----------------------------------
# Core Tax Logic
# -----------------------------------

def calculate_progressive_tax(
    taxable_income: float,
    brackets: List[tuple]
) -> List[TaxBracketDetail]:
    tax_details = []
    remaining_income = taxable_income

    for i in range(len(brackets)):
        bracket_start, rate = brackets[i]
        bracket_end = (
            brackets[i + 1][0] if i + 1 < len(brackets) else None
        )

        if remaining_income <= 0:
            break

        taxable_at_rate = (
            min(remaining_income, bracket_end - bracket_start)
            if bracket_end
            else remaining_income
        )

        tax = taxable_at_rate * rate
        tax_details.append(
            TaxBracketDetail(
                bracket_start=bracket_start,
                rate=rate,
                taxed_amount=taxable_at_rate,
                tax=round(tax, 2),
            )
        )

        remaining_income -= taxable_at_rate

    return tax_details

# -----------------------------------
# Endpoints
# -----------------------------------

@app.post("/tax/calculate", response_model=TaxCalculationResponse)
def calculate_federal_tax(payload: TaxCalculationRequest):
    if payload.tax_year != 2024:
        raise HTTPException(
            status_code=400,
            detail="Only 2024 tax year currently supported"
        )

    # Gross Income
    gross_income = sum(i.amount for i in payload.incomes)

    # Adjusted Gross Income (AGI)
    # (Above-the-line deductions would go here)
    adjusted_gross_income = gross_income

    # Deduction Selection
    standard_deduction = STANDARD_DEDUCTION_2024[payload.filing_status]
    itemized_total = (
        sum(d.amount for d in payload.itemized_deductions)
        if payload.itemized_deductions
        else 0
    )

    deduction_used = max(standard_deduction, itemized_total)

    # Taxable Income
    taxable_income = max(adjusted_gross_income - deduction_used, 0)

    # Progressive Tax Calculation
    brackets = FEDERAL_TAX_BRACKETS_2024[payload.filing_status]
    bracket_details = calculate_progressive_tax(
        taxable_income, brackets
    )

    total_tax = sum(b.tax for b in bracket_details)

    # Credits (non-refundable simplified)
    credits_applied = min(payload.credits, total_tax)

    total_liability = round(total_tax - credits_applied, 2)

    return TaxCalculationResponse(
        gross_income=round(gross_income, 2),
        adjusted_gross_income=round(adjusted_gross_income, 2),
        deduction_used=round(deduction_used, 2),
        taxable_income=round(taxable_income, 2),
        bracket_breakdown=bracket_details,
        total_tax_before_credits=round(total_tax, 2),
        credits_applied=round(credits_applied, 2),
        total_tax_liability=total_liability,
        explanation=(
            "Federal income tax calculated using 2024 IRS progressive "
            "tax brackets and the greater of standard or itemized deductions."
        ),
    )

@app.get("/health")
def health_check():
    return {"status": "ok"}


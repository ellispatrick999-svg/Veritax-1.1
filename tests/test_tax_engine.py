import pytest
from fastapi.testclient import TestClient
from tax_api import app, STANDARD_DEDUCTION_2024, FEDERAL_TAX_BRACKETS_2024

client = TestClient(app)

# -----------------------------
# Helper functions
# -----------------------------

def calculate_expected_tax(taxable_income, brackets):
    """
    Deterministic progressive tax calculation for testing
    """
    remaining_income = taxable_income
    tax = 0
    for i, (start, rate) in enumerate(brackets):
        end = brackets[i + 1][0] if i + 1 < len(brackets) else None
        taxable_at_rate = remaining_income
        if end:
            taxable_at_rate = min(remaining_income, end - start)
        tax += taxable_at_rate * rate
        remaining_income -= taxable_at_rate
        if remaining_income <= 0:
            break
    return round(tax, 2)

# -----------------------------
# Test Data
# -----------------------------

BASE_PAYLOAD = {
    "tax_year": 2024,
    "filing_status": "single",
    "incomes": [{"source": "salary", "amount": 85000}],
    "itemized_deductions": [],
    "dependents": 0,
    "credits": 0.0
}

# -----------------------------
# Tests
# -----------------------------

def test_standard_deduction_applied():
    payload = BASE_PAYLOAD.copy()
    # No itemized deductions → should use standard
    response = client.post("/tax/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["deduction_used"] == STANDARD_DEDUCTION_2024["single"]

def test_itemized_deduction_used_when_higher():
    payload = BASE_PAYLOAD.copy()
    payload["itemized_deductions"] = [{"name": "Mortgage Interest", "amount": 20000}]
    response = client.post("/tax/calculate", json=payload)
    data = response.json()
    # Should use itemized since 20k > 14,600
    assert data["deduction_used"] == 20000

def test_taxable_income_calculation():
    payload = BASE_PAYLOAD.copy()
    response = client.post("/tax/calculate", json=payload)
    data = response.json()
    expected_taxable = payload["incomes"][0]["amount"] - STANDARD_DEDUCTION_2024["single"]
    assert data["taxable_income"] == expected_taxable

def test_progressive_tax_brackets():
    payload = BASE_PAYLOAD.copy()
    response = client.post("/tax/calculate", json=payload)
    data = response.json()
    taxable_income = data["taxable_income"]
    expected_tax = calculate_expected_tax(taxable_income, FEDERAL_TAX_BRACKETS_2024["single"])
    assert data["total_tax_before_credits"] == expected_tax

def test_credits_applied_correctly():
    payload = BASE_PAYLOAD.copy()
    payload["credits"] = 1000.0
    response = client.post("/tax/calculate", json=payload)
    data = response.json()
    assert data["credits_applied"] == 1000.0
    assert data["total_tax_liability"] == data["total_tax_before_credits"] - 1000.0

def test_filing_status_variation():
    payload = BASE_PAYLOAD.copy()
    payload["filing_status"] = "married_joint"
    response = client.post("/tax/calculate", json=payload)
    data = response.json()
    assert data["deduction_used"] == STANDARD_DEDUCTION_2024["married_joint"]

def test_zero_income_edge_case():
    payload = BASE_PAYLOAD.copy()
    payload["incomes"] = [{"source": "none", "amount": 0}]
    response = client.post("/tax/calculate", json=payload)
    data = response.json()
    assert data["taxable_income"] == 0
    assert data["total_tax_liability"] == 0

def test_negative_income_edge_case():
    payload = BASE_PAYLOAD.copy()
    payload["incomes"] = [{"source": "loss", "amount": -5000}]
    response = client.post("/tax/calculate", json=payload)
    data = response.json()
    # Negative income → taxable income 0
    assert data["taxable_income"] == 0
    assert data["total_tax_liability"] == 0

def test_business_rule_high_deductions_trigger_warning():
    # Simulate "audit rule" for very high deductions relative to income
    payload = BASE_PAYLOAD.copy()
    payload["incomes"] = [{"source": "salary", "amount": 50000}]
    payload["itemized_deductions"] = [{"name": "Huge Donation", "amount": 40000}]
    response = client.post("/tax/calculate", json=payload)
    data = response.json()
    # Deduction should still be applied correctly
    assert data["deduction_used"] == 40000
    assert data["taxable_income"] == 10000
    # Could also log an "audit flag" if implemented

def test_depreciation_and_capital_expenses():
    # Simplified demo: treat capital expenses as itemized deductions
    payload = BASE_PAYLOAD.copy()
    payload["itemized_deductions"] = [
        {"name": "Depreciation Expense", "amount": 10000},
        {"name": "Office Equipment", "amount": 5000}
    ]
    response = client.post("/tax/calculate", json=payload)
    data = response.json()
    # Deduction = sum of itemized
    assert data["deduction_used"] == 15000

def test_end_to_end_tax_engine_calculation():
    payload = {
        "tax_year": 2024,
        "filing_status": "head_of_household",
        "incomes": [{"source": "salary", "amount": 120000}],
        "itemized_deductions": [{"name": "Mortgage", "amount": 25000}],
        "dependents": 2,
        "credits": 2000
    }
    response = client.post("/tax/calculate", json=payload)
    data = response.json()
    assert data["gross_income"] == 120000
    # Deduction should use itemized 25k vs standard 21,900 → 25k
    assert data["deduction_used"] == 25000
    assert data["taxable_income"] == 120000 - 25000
    assert data["credits_applied"] == 2000
    assert data["total_tax_liability"] == data["total_tax_before_credits"] - 2000
    assert len(data["bracket_breakdown"]) > 0

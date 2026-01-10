import pytest
from data_ingestion import load_user_data, validate_user_data, parse_w2_form, parse_1099_form

# -----------------------------------
# Sample Input Data
# -----------------------------------

VALID_USER_DATA = {
    "user_id": "user123",
    "name": "John Doe",
    "ssn": "123-45-6789",
    "filing_status": "single",
    "incomes": [{"source": "salary", "amount": 85000}],
    "itemized_deductions": [],
    "dependents": 0,
    "credits": 0
}

MISSING_FIELDS_USER_DATA = {
    "user_id": "user456",
    "name": "Jane Smith",
    # Missing SSN
    "filing_status": "married_joint",
    "incomes": [{"source": "salary", "amount": 95000}],
}

INVALID_FIELDS_USER_DATA = {
    "user_id": "user789",
    "name": "Alice Johnson",
    "ssn": "123456789",  # Invalid format
    "filing_status": "single",
    "incomes": [{"source": "salary", "amount": -5000}],  # Negative income
}

# Mock W-2 and 1099 data (simplified)
MOCK_W2 = {
    "employer": "ACME Corp",
    "wages": 85000,
    "federal_income_tax": 15000,
    "ss_tax": 5200,
    "medicare_tax": 1232
}

MOCK_1099 = {
    "payer": "Freelance Client",
    "nonemployee_comp": 12000,
    "federal_income_tax": 1800
}

# -----------------------------------
# Tests
# -----------------------------------

def test_load_valid_user_data():
    """
    Confirm that valid user data is loaded correctly
    """
    data = load_user_data(VALID_USER_DATA)
    assert isinstance(data, dict)
    assert data["user_id"] == "user123"
    assert "incomes" in data
    assert data["filing_status"] == "single"

def test_missing_fields_detected():
    """
    Validate that missing required fields (like SSN) are flagged
    """
    data = load_user_data(MISSING_FIELDS_USER_DATA)
    errors = validate_user_data(data)
    assert "ssn" in errors
    assert errors["ssn"] == "Missing required field"

def test_invalid_fields_detected():
    """
    Detect invalid formats and negative values
    """
    data = load_user_data(INVALID_FIELDS_USER_DATA)
    errors = validate_user_data(data)
    assert "ssn" in errors
    assert errors["ssn"] == "Invalid format"
    assert "incomes" in errors
    assert errors["incomes"][0]["amount"] < 0

def test_w2_parsing_extracts_fields():
    """
    Test that W2 form data is parsed into structured format
    """
    parsed = parse_w2_form(MOCK_W2)
    assert parsed["employer"] == "ACME Corp"
    assert parsed["wages"] == 85000
    assert parsed["federal_income_tax"] == 15000
    assert "ss_tax" in parsed
    assert "medicare_tax" in parsed

def test_1099_parsing_extracts_fields():
    """
    Test that 1099 form data is parsed correctly
    """
    parsed = parse_1099_form(MOCK_1099)
    assert parsed["payer"] == "Freelance Client"
    assert parsed["nonemployee_comp"] == 12000
    assert parsed["federal_income_tax"] == 1800

def test_combined_income_extraction():
    """
    Confirm that multiple income sources (W2 + 1099) are combined correctly
    """
    w2_data = parse_w2_form(MOCK_W2)
    form1099_data = parse_1099_form(MOCK_1099)
    total_income = sum([w2_data["wages"], form1099_data["nonemployee_comp"]])
    assert total_income == 85000 + 12000

def test_invalid_form_data_raises_errors():
    """
    Ensure invalid form fields raise validation errors
    """
    invalid_w2 = MOCK_W2.copy()
    invalid_w2["wages"] = -50000
    with pytest.raises(ValueError):
        parse_w2_form(invalid_w2)

    invalid_1099 = MOCK_1099.copy()
    invalid_1099["nonemployee_comp"] = "twelve thousand"
    with pytest.raises(ValueError):
        parse_1099_form(invalid_1099)


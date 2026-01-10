import pytest
from fastapi.testclient import TestClient
from ai_api import app as ai_app
from tax_api import app as tax_app
from user_api import app as user_app
from auth import app as auth_app
from settings import CONFIG

# -----------------------------
# Setup Test Clients
# -----------------------------

ai_client = TestClient(ai_app)
tax_client = TestClient(tax_app)
user_client = TestClient(user_app)
auth_client = TestClient(auth_app)

# -----------------------------
# Test Data
# -----------------------------

USER_PROFILE_PAYLOAD = {
    "user_id": "user123",
    "name": "John Doe",
    "email": "john@example.com",
    "filing_status": "single",
    "income": 85000
}

REASONING_QUESTION = "Am I eligible for the standard deduction?"
TAX_CALC_PAYLOAD = {
    "tax_year": 2024,
    "filing_status": "single",
    "incomes": [{"source": "salary", "amount": 85000}],
    "itemized_deductions": [],
    "credits": 0
}

AUTH_PAYLOAD = {
    "username": "testuser",
    "password": "password123"
}

# -----------------------------
# Reasoning API Tests
# -----------------------------

def test_reasoning_endpoint_returns_answer():
    response = ai_client.post("/reason", json={"question": REASONING_QUESTION, "user_context": USER_PROFILE_PAYLOAD})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "reasoning_steps" in data
    assert isinstance(data["reasoning_steps"], list)

# -----------------------------
# Tax Calculation API Tests
# -----------------------------

def test_tax_calculation_endpoint_returns_expected_keys():
    response = tax_client.post("/tax/calculate", json=TAX_CALC_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    expected_keys = ["gross_income", "deduction_used", "taxable_income", "total_tax_before_credits", "credits_applied", "total_tax_liability", "bracket_breakdown"]
    for key in expected_keys:
        assert key in data

def test_tax_calculation_handles_zero_income():
    payload = TAX_CALC_PAYLOAD.copy()
    payload["incomes"] = [{"source": "salary", "amount": 0}]
    response = tax_client.post("/tax/calculate", json=payload)
    data = response.json()
    assert data["total_tax_liability"] == 0

# -----------------------------
# User Profile API Tests
# -----------------------------

def test_create_user_profile():
    response = user_client.post("/user/create", json=USER_PROFILE_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == USER_PROFILE_PAYLOAD["user_id"]
    assert "name" in data
    assert "filing_status" in data

def test_get_user_profile():
    user_client.post("/user/create", json=USER_PROFILE_PAYLOAD)
    response = user_client.get(f"/user/{USER_PROFILE_PAYLOAD['user_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == USER_PROFILE_PAYLOAD["user_id"]

# -----------------------------
# Authentication API Tests
# -----------------------------

def test_register_and_login_user():
    # Register
    response = auth_client.post("/auth/register", json=AUTH_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert "username" in data

    # Login
    response = auth_client.post("/auth/login", json=AUTH_PAYLOAD)
    assert response.status_code == 200
    login_data = response.json()
    assert "access_token" in login_data
    assert "token_type" in login_data

def test_authentication_fails_invalid_password():
    response = auth_client.post("/auth/login", json={"username": AUTH_PAYLOAD["username"], "password": "wrongpassword"})
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid credentials"

# -----------------------------
# Configuration / Settings Tests
# -----------------------------

def test_configuration_values_exist():
    assert "SECRET_KEY" in CONFIG
    assert isinstance(CONFIG["SECRET_KEY"], str)
    assert CONFIG.get("TAX_YEAR") == 2024
    assert "AI_MODEL" in CONFIG

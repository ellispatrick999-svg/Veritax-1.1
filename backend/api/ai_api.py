from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import uuid

# -----------------------------------
# App initialization
# -----------------------------------

app = FastAPI(
    title="AI Tax Reasoning Engine",
    version="0.1.0",
    description="AI-powered reasoning endpoints for tax and filing assistance"
)

# -----------------------------------
# Request / Response Models
# -----------------------------------

class ReasoningRequest(BaseModel):
    user_id: Optional[str] = None
    context: Dict[str, Any] = Field(
        ..., description="User financial/tax context"
    )
    question: str = Field(
        ..., description="User's tax or filing question"
    )

class ReasoningResponse(BaseModel):
    request_id: str
    answer: str
    reasoning_steps: Optional[list[str]] = None
    confidence: float

class TaxCalculationRequest(BaseModel):
    income: float
    deductions: float
    filing_status: str

class TaxCalculationResponse(BaseModel):
    taxable_income: float
    estimated_tax: float
    explanation: str

# -----------------------------------
# Core Reasoning Engine (LLM wrapper)
# -----------------------------------

def run_reasoning_engine(question: str, context: Dict[str, Any]) -> dict:
    """
    This is where your LLM or hybrid rules + AI logic lives.
    Replace with OpenAI / Azure / Local model calls.
    """

    # Example deterministic pre-reasoning
    income = context.get("income", 0)
    filing_status = context.get("filing_status", "unknown")

    # Mock AI reasoning (replace with real LLM output)
    reasoning_steps = [
        f"Identified filing status as {filing_status}",
        f"Reviewed reported income of {income}",
        "Checked applicable tax rules",
        "Generated user-facing explanation"
    ]

    answer = (
        "Based on the information provided, you may be eligible for "
        "standard deductions and should review potential credits."
    )

    return {
        "answer": answer,
        "reasoning_steps": reasoning_steps,
        "confidence": 0.81
    }

# -----------------------------------
# Endpoints
# -----------------------------------

@app.post("/reasoning", response_model=ReasoningResponse)
def reasoning_endpoint(payload: ReasoningRequest):
    """
    General-purpose AI reasoning endpoint for tax questions.
    """

    request_id = str(uuid.uuid4())

    try:
        result = run_reasoning_engine(
            question=payload.question,
            context=payload.context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ReasoningResponse(
        request_id=request_id,
        answer=result["answer"],
        reasoning_steps=result.get("reasoning_steps"),
        confidence=result["confidence"]
    )

@app.post("/tax/calculate", response_model=TaxCalculationResponse)
def calculate_tax(payload: TaxCalculationRequest):
    """
    Deterministic tax calculation (non-AI).
    """

    taxable_income = max(payload.income - payload.deductions, 0)

    # VERY simplified example (replace with real brackets)
    if payload.filing_status.lower() == "single":
        tax_rate = 0.22
    else:
        tax_rate = 0.18

    estimated_tax = taxable_income * tax_rate

    return TaxCalculationResponse(
        taxable_income=taxable_income,
        estimated_tax=estimated_tax,
        explanation=(
            f"Tax calculated using a {tax_rate*100}% rate based on "
            f"{payload.filing_status} filing status."
        )
    )

@app.get("/health")
def health_check():
    return {"status": "ok"}

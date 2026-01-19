from pydantic import BaseModel
from typing import Optional, List

class APIError(BaseModel):
    code: str
    message: str
    request_id: Optional[str]


class TaxCalculationRequest(BaseModel):
    income: float
    filing_status: str
    deductions: Optional[float] = 0.0


class TaxCalculationResponse(BaseModel):
    tax_liability: float
    effective_rate: float

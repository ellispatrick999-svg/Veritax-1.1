# backend/data/schema.py
from dataclasses import dataclass, field
from datetime import date
from typing import Optional, Literal
from uuid import UUID, uuid4

ExpenseCategory = Literal[
    "meals",
    "travel",
    "office_supplies",
    "software",
    "rent",
    "utilities",
    "other"
]

@dataclass
class FinancialRecord:
    id: UUID = field(default_factory=uuid4)
    source_document_id: Optional[str] = None
    merchant: Optional[str] = None
    amount: float = 0.0
    currency: str = "USD"
    date: Optional[date] = None
    category: ExpenseCategory = "other"
    deductible: bool = False
    confidence: float = 0.0  # 0–1

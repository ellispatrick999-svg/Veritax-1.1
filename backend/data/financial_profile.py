from dataclasses import dataclass
from typing import List
from .tax_forms.w2_model import W2
from .tax_forms.form1099_model import Form1099


@dataclass
class FinancialProfile:
    user_id: str
    w2_forms: List[W2]
    form1099s: List[Form1099]
    deductions: float = 0.0
    dependents: int = 0

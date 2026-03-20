from typing import Dict, Any


class TaxEngine:

    def calculate(self, financial_profile: Dict[str, Any]) -> Dict[str, Any]:

        income = financial_profile.get("income", 0)
        deductions = financial_profile.get("deductions", {}).get("total", 0)

        taxable_income = max(income - deductions, 0)
        tax = taxable_income * 0.2  # placeholder

        return {
            "source": "tax_engine",
            "data": {
                "taxable_income": taxable_income,
                "estimated_tax": tax
            },
            "confidence": 0.9
        }

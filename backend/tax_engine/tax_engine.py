from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

from depreciation import DepreciableAsset, AssetPool, depreciate_pool
from audit_rules import run_audit, AuditResult


# =====================================================
# FORM MODELS
# =====================================================

@dataclass
class W2:
    employer_ein: str
    wages: float
    federal_withheld: float
    state_withheld: float


@dataclass
class Form1099NEC:
    payer_tin: str
    nonemployee_comp: float


@dataclass
class Form1099INT:
    payer_tin: str
    interest_income: float


@dataclass
class Form1099DIV:
    payer_tin: str
    ordinary_dividends: float


@dataclass
class ScheduleC:
    gross_receipts: float
    expenses: float


TaxForm = Union[
    W2,
    Form1099NEC,
    Form1099INT,
    Form1099DIV,
    ScheduleC
]


# =====================================================
# TAXPAYER MODEL
# =====================================================

@dataclass
class Taxpayer:
    taxpayer_id: str
    filing_status: str
    forms: List[TaxForm] = field(default_factory=list)
    assets: List[DepreciableAsset] = field(default_factory=list)
    itemized_deductions: float = 0.0
    prior_year_depreciation: Optional[float] = None


# =====================================================
# NORMALIZATION LAYER
# =====================================================

class IncomeNormalizer:
    def __init__(self, forms: List[TaxForm]):
        self.forms = forms

    def normalize(self) -> Dict[str, float]:
        buckets = {
            "wages": 0.0,
            "self_employment": 0.0,
            "interest": 0.0,
            "dividends": 0.0,
            "business_income": 0.0,
            "withholding_federal": 0.0,
            "withholding_state": 0.0,
        }

        for f in self.forms:
            if isinstance(f, W2):
                buckets["wages"] += f.wages
                buckets["withholding_federal"] += f.federal_withheld
                buckets["withholding_state"] += f.state_withheld

            elif isinstance(f, Form1099NEC):
                buckets["self_employment"] += f.nonemployee_comp

            elif isinstance(f, ScheduleC):
                buckets["business_income"] += (
                    f.gross_receipts - f.expenses
                )

            elif isinstance(f, Form1099INT):
                buckets["interest"] += f.interest_income

            elif isinstance(f, Form1099DIV):
                buckets["dividends"] += f.ordinary_dividends

        return buckets


# =====================================================
# TAX COMPUTATION HELPERS
# =====================================================

STANDARD_DEDUCTION = {
    "SINGLE": 14600,
    "MARRIED_JOINT": 29200,
    "HEAD_OF_HOUSEHOLD": 21900,
}


def compute_se_tax(net_se_income: float) -> float:
    """
    Simplified SE tax:
    92.35% * 15.3%
    """
    if net_se_income <= 0:
        return 0.0

    se_tax_base = net_se_income * 0.9235
    return round(se_tax_base * 0.153, 2)


# =====================================================
# TAX ENGINE CORE
# =====================================================

class TaxEngine:
    def __init__(
        self,
        tax_config: Dict,
        audit_config: Dict
    ):
        self.tax_config = tax_config
        self.audit_config = audit_config

    # -------------------------------------------------
    # INCOME
    # -------------------------------------------------

    def compute_income(self, taxpayer: Taxpayer) -> Dict:
        normalizer = IncomeNormalizer(taxpayer.forms)
        income = normalizer.normalize()

        income["total_income"] = round(
            income["wages"]
            + income["self_employment"]
            + income["business_income"]
            + income["interest"]
            + income["dividends"],
            2
        )

        return income

    # -------------------------------------------------
    # DEDUCTIONS
    # -------------------------------------------------

    def compute_deductions(self, taxpayer: Taxpayer) -> Dict:
        standard = STANDARD_DEDUCTION.get(
            taxpayer.filing_status, 0
        )

        deduction_used = max(
            standard,
            taxpayer.itemized_deductions
        )

        return {
            "standard_deduction": standard,
            "itemized_deductions": taxpayer.itemized_deductions,
            "deduction_taken": deduction_used,
        }

    # -------------------------------------------------
    # DEPRECIATION
    # -------------------------------------------------

    def compute_depreciation(self, taxpayer: Taxpayer) -> Dict:
        pool = AssetPool(assets=taxpayer.assets)
        return depreciate_pool(pool, self.tax_config)

    # -------------------------------------------------
    # AUDIT RISK
    # -------------------------------------------------

    def compute_audit_risk(
        self,
        depreciation_result: Dict,
        taxpayer: Taxpayer
    ) -> AuditResult:

        return run_audit(
            federal_assets=depreciation_result["federal"],
            state_assets=depreciation_result["state"],
            config=self.audit_config,
            prior_year_depreciation=taxpayer.prior_year_depreciation
        )

    # -------------------------------------------------
    # FULL RETURN PIPELINE
    # -------------------------------------------------

    def run_return(self, taxpayer: Taxpayer) -> Dict:
        income = self.compute_income(taxpayer)
        deductions = self.compute_deductions(taxpayer)
        depreciation = self.compute_depreciation(taxpayer)

        se_tax = compute_se_tax(
            income["self_employment"] + income["business_income"]
        )

        taxable_income = max(
            0.0,
            income["total_income"] - deductions["deduction_taken"]
        )

        audit = self.compute_audit_risk(depreciation, taxpayer)

        return {
            "taxpayer_id": taxpayer.taxpayer_id,
            "filing_status": taxpayer.filing_status,
            "income": income,
            "deductions": deductions,
            "self_employment_tax": se_tax,
            "taxable_income": round(taxable_income, 2),
            "depreciation": depreciation,
            "audit": {
                "risk_score": audit.total_score,
                "risk_level": audit.risk_level,
                "flags": [
                    {
                        "code": f.code,
                        "description": f.description,
                        "severity": f.severity,
                    }
                    for f in audit.flags
                ],
            },
        }


# =====================================================
# INTEGRATION TEST
# =====================================================

if __name__ == "__main__":
    taxpayer = Taxpayer(
        taxpayer_id="123-45-6789",
        filing_status="SINGLE",
        forms=[
            W2("12-3456789", 85000, 12000, 3500),
            Form1099NEC("98-7654321", 22000),
            ScheduleC(50000, 18000),
            Form1099INT("11-2223333", 450),
        ],
        assets=[
            DepreciableAsset(
                cost=100000,
                recovery_period=5,
                placed_in_service_qtr=4,
                section179=25000
            )
        ],
        itemized_deductions=9000,
        prior_year_depreciation=18000
    )

    engine = TaxEngine(
        tax_config={
            "bonus_rate": 0.60,
            "state_bonus_rate": 0.00
        },
        audit_config={
            "section179_soft_limit": 1_000_000
        }
    )

    result = engine.run_return(taxpayer)
    print(result)


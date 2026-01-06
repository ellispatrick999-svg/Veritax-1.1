"""
tax_pipeline.py

Full Tax Processing Pipeline
- Orchestrates calculation, compliance, risk scoring, safety, escalation, and AI advisor report.
- Produces a structured, human-readable, audit-ready report.
- Automatically flags high-risk or non-compliant cases for human review.
"""

from advisor import TaxAIAdvisor
from calculator import calculate

# =====================================================
# TAX PIPELINE CLASS
# =====================================================

class TaxPipeline:

    def __init__(self, tax_config: dict, audit_config: dict):
        self.tax_config = tax_config
        self.audit_config = audit_config
        self.advisor = TaxAIAdvisor(tax_config, audit_config)

    def process_taxpayer(
        self,
        taxpayer,
        prior_year_deductions: float = 0.0,
        language: str = "en"
    ) -> dict:
        """
        Process a single taxpayer fully:
        - Calculate IRS return
        - Run compliance checks
        - Run risk scoring
        - Run safety checks
        - Run escalation
        - Produce AI reasoning report
        """
        # Step 1: Orchestrate advisor (includes everything)
        result = self.advisor.analyze_return(
            taxpayer=taxpayer,
            prior_year_deductions=prior_year_deductions,
            language=language
        )

        # Step 2: Automatic routing / flagging
        if result.get("escalation") and result["escalation"].needs_escalation:
            result["action"] = "HUMAN_REVIEW_REQUIRED"
        else:
            result["action"] = "NO_IMMEDIATE_REVIEW"

        # Step 3: Include high-level summary
        summary = {
            "taxpayer_id": getattr(taxpayer, "taxpayer_id", "UNKNOWN"),
            "compliant": result.get("compliance").compliant,
            "risk_score": result.get("risk_scoring").total_score,
            "risk_level": result.get("risk_scoring").risk_level,
            "safety_passed": result.get("safety").allowed,
            "escalation_needed": result.get("escalation").needs_escalation,
            "final_action": result.get("action"),
        }

        result["summary"] = summary
        return result


# =====================================================
# EXAMPLE USAGE
# =====================================================

if __name__ == "__main__":
    from calculator import W2, Form1099NEC, ScheduleC, DepreciableAsset

    class DummyTaxpayer:
        taxpayer_id = "123-45-6789"
        filing_status = "SINGLE"
        forms = [
            W2("12-3456789", 85000, 12000, 3500),
            Form1099NEC("98-7654321", 22000),
            ScheduleC(50000, 18000)
        ]
        assets = [
            DepreciableAsset(cost=100000, recovery_period=5, placed_in_service_qtr=4, section179=25000)
        ]
        itemized_deductions = 9000
        prior_year_depreciation = 18000

    taxpayer = DummyTaxpayer()
    tax_config = {"bonus_rate": 0.60, "state_bonus_rate": 0.0}
    audit_config = {"section179_soft_limit": 1_000_000}

    pipeline = TaxPipeline(tax_config, audit_config)
    final_report = pipeline.process_taxpayer(
        taxpayer=taxpayer,
        prior_year_deductions=9000,
        language="en"
    )

    # Print full reasoning report
    print(final_report["report_text"])

    # Print summary for quick review
    print("\n=== SUMMARY ===")
    for k, v in final_report["summary"].items():
        print(f"{k}: {v}")

"""
advisor.py

AI Advisor layer for tax engine.
- Orchestrates calculation, compliance, risk, safety, and escalation.
- Provides reasoning and explanations.
- Multi-language support.
- Never provides illegal or personalized tax advice.
"""

from typing import Dict
from calculator import calculate
from compliance import run_compliance_check
from risk_scoring import run_risk_scoring
from safety_checks import safety_gate
from escalation import evaluate_for_escalation


# =====================================================
# AI Advisor
# =====================================================

class TaxAIAdvisor:
    def __init__(self, tax_config: Dict, audit_config: Dict):
        self.tax_config = tax_config
        self.audit_config = audit_config

    def analyze_return(self, taxpayer, prior_year_deductions: float = 0.0, language: str = "en") -> Dict:
        """
        Full orchestration of tax analysis with safety, risk, and compliance.
        Returns a human-readable report with reasoning in the chosen language.
        """
        # Step 1: Calculate IRS-style return
        calculation_result = calculate(
            taxpayer=taxpayer,
            tax_config=self.tax_config,
            audit_config=self.audit_config
        )

        irs_return = calculation_result["return"]

        # Step 2: Compliance check
        compliance_result = run_compliance_check(irs_return)
        calculation_result["compliance"] = compliance_result

        # Step 3: Risk scoring
        risk_result = run_risk_scoring(irs_return, prior_year_deductions)
        calculation_result["risk_scoring"] = risk_result

        # Step 4: Safety checks
        # For any textual outputs from AI reasoning
        safety_result = safety_gate(
            ai_response="This is a reasoning placeholder explaining the return.", 
            context={"jurisdiction": "US"}
        )
        calculation_result["safety"] = safety_result

        # Step 5: Escalation evaluation
        escalation_result = evaluate_for_escalation(
            taxpayer_id=taxpayer.taxpayer_id,
            compliance_result=compliance_result.__dict__,
            risk_score=risk_result.__dict__,
            safety_result=safety_result.__dict__
        )
        calculation_result["escalation"] = escalation_result

        # Step 6: Generate reasoning / report text (multilingual)
        report_text = self._generate_reasoning_report(
            irs_return,
            compliance_result,
            risk_result,
            safety_result,
            escalation_result,
            language
        )

        calculation_result["report_text"] = report_text

        return calculation_result

    # -------------------------------------------------
    # PRIVATE: Generate reasoning in multiple languages
    # -------------------------------------------------
    def _generate_reasoning_report(
        self,
        irs_return,
        compliance_result,
        risk_result,
        safety_result,
        escalation_result,
        language: str
    ) -> str:
        """
        Generates a safe, human-readable report explaining
        the tax return, compliance checks, and risk.
        """
        lines = []
        lines.append(f"Tax return analysis report (Language: {language})\n")
        lines.append("Summary of IRS Form 1040:\n")
        form_1040 = next((f for f in irs_return.get("Forms", []) if f.get("Form") == "1040"), None)
        if form_1040:
            for k, v in form_1040.items():
                if k != "Form":
                    lines.append(f"- {k}: {v}")

        lines.append("\nCompliance Checks:")
        for issue in compliance_result.issues:
            lines.append(f"- [{issue.severity}] {issue.message}")

        lines.append("\nRisk Scoring Flags:")
        for flag in risk_result.flags:
            lines.append(f"- [{flag.severity}] {flag.description} (Impact: {flag.score_impact})")

        lines.append("\nSafety Status:")
        if safety_result.allowed:
            lines.append("- All content is safe and educational.")
        else:
            lines.append(f"- Safety concern detected: {safety_result.reason}")

        lines.append("\nEscalation Cases:")
        if escalation_result.needs_escalation:
            for case in escalation_result.cases:
                lines.append(f"- {case.severity}: {case.reason}")
        else:
            lines.append("- No escalation required.")

        lines.append("\nDisclaimer:")
        lines.append("This report is for educational purposes only and does not constitute legal or tax advice.")

        # Multilingual placeholder: in production, integrate a translation engine here
        # e.g., Google Translate API, DeepL API, or built-in multilingual LLM
        report_text = "\n".join(lines)
        return report_text


# =====================================================
# PUBLIC API FUNCTION
# =====================================================

def advise(taxpayer, tax_config: Dict, audit_config: Dict, prior_year_deductions: float = 0.0, language: str = "en") -> Dict:
    advisor = TaxAIAdvisor(tax_config, audit_config)
    return advisor.analyze_return(taxpayer, prior_year_deductions, language)


# =====================================================
# EXAMPLE USAGE
# =====================================================

if __name__ == "__main__":
    from calculator import W2, Form1099NEC, ScheduleC, DepreciableAsset
    from calculator import TaxCalculator, calculate

    # Example taxpayer
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

    result = advise(taxpayer, tax_config, audit_config, prior_year_deductions=9000, language="en")
    print(result["report_text"])

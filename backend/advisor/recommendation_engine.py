"""
recommendation_engine.py

Educational Recommendation Engine
- Provides general, safe recommendations based on tax rules.
- Highlights areas for review and general strategies.
- Fully compliant: does NOT give personalized tax advice.
- Integrates compliance, risk, and safety.
"""

from typing import Dict, List
from risk_scoring import run_risk_scoring
from compliance import run_compliance_check
from safety_checks import safety_gate


class RecommendationEngine:
    def __init__(self):
        self.notes: List[str] = []

    def generate_recommendations(self, irs_return: Dict, prior_year_deductions: float = 0.0) -> List[str]:
        """
        Generate safe, educational recommendations based on the IRS return.
        """
        self.notes.clear()

        # Step 1: Run compliance checks
        compliance_result = run_compliance_check(irs_return)
        if not compliance_result.compliant:
            self.notes.append(
                "Review areas flagged in compliance checks; ensure all required fields and forms are completed correctly."
            )

        # Step 2: Run risk scoring
        risk_result = run_risk_scoring(irs_return, prior_year_deductions)
        if risk_result.risk_level in ("HIGH", "SEVERE"):
            self.notes.append(
                f"Risk scoring indicates a {risk_result.risk_level} risk. Consider reviewing flagged items carefully."
            )

        # Step 3: Run safety checks
        safety_result = safety_gate(
            ai_response="Educational recommendation placeholder", 
            context={"jurisdiction": "US"}
        )
        if not safety_result.allowed:
            self.notes.append(
                f"Safety check flagged potential unsafe content: {safety_result.reason}"
            )

        # Step 4: General educational suggestions
        self.notes.append(
            "Educational Note: Section 179 and bonus depreciation can affect business property deductions. "
            "All limits and eligibility rules must be followed."
        )
        self.notes.append(
            "Educational Note: Standard vs itemized deductions are available to all taxpayers. "
            "Choose the option that complies with IRS rules."
        )
        self.notes.append(
            "Educational Note: Schedule C reports business income and expenses. "
            "Losses and deductions are subject to IRS regulations."
        )
        self.notes.append(
            "Reminder: Always consult a licensed tax professional or CPA for personalized guidance."
        )

        return self.notes


# =====================================================
# PUBLIC API
# =====================================================

def recommend(irs_return: Dict, prior_year_deductions: float = 0.0) -> List[str]:
    """
    Entry point for safe recommendations.
    """
    engine = RecommendationEngine()
    return engine.generate_recommendations(irs_return, prior_year_deductions)


# =====================================================
# EXAMPLE USAGE
# =====================================================

if __name__ == "__main__":
    example_return = {
        "Forms": [
            {"Form": "1040", "Line 9": 100000, "

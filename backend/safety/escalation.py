"""
escalation.py

Routes uncertain, high-risk, or non-compliant tax return cases
to human review. This ensures that no ambiguous or risky
decisions are automatically finalized.

This module integrates:
- Compliance results
- Risk scoring
- Safety checks
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


# =====================================================
# MODELS
# =====================================================

@dataclass
class EscalationCase:
    taxpayer_id: str
    reason: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    related_flags: Optional[List[Dict]] = None
    notes: Optional[str] = None


@dataclass
class EscalationResult:
    needs_escalation: bool
    cases: List[EscalationCase]


# =====================================================
# ESCALATION RULES
# =====================================================

class EscalationEngine:

    def __init__(self):
        self.cases: List[EscalationCase] = []

    # -------------------------------------------------
    # Compliance-based escalation
    # -------------------------------------------------
    def check_compliance(self, taxpayer_id: str, compliance_result: Dict):
        if not compliance_result.get("compliant", True):
            errors = [
                issue["message"]
                for issue in compliance_result.get("issues", [])
                if issue.get("severity") == "ERROR"
            ]
            if errors:
                self.cases.append(
                    EscalationCase(
                        taxpayer_id=taxpayer_id,
                        reason="Compliance validation failure",
                        severity="CRITICAL",
                        related_flags=[{"message": e} for e in errors],
                        notes="Return violates IRS structural rules"
                    )
                )

    # -------------------------------------------------
    # Risk-based escalation
    # -------------------------------------------------
    def check_risk(self, taxpayer_id: str, risk_score: Dict):
        score = risk_score.get("total_score", 0)
        level = risk_score.get("risk_level", "LOW")
        flags = risk_score.get("flags", [])

        if level in ("HIGH", "SEVERE") or score >= 50:
            self.cases.append(
                EscalationCase(
                    taxpayer_id=taxpayer_id,
                    reason="High deduction or audit risk",
                    severity="HIGH" if level == "HIGH" else "CRITICAL",
                    related_flags=flags,
                    notes=f"Total risk score: {score}, risk level: {level}"
                )
            )

    # -------------------------------------------------
    # Safety-based escalation
    # -------------------------------------------------
    def check_safety(self, taxpayer_id: str, safety_result: Dict):
        if not safety_result.get("allowed", True):
            self.cases.append(
                EscalationCase(
                    taxpayer_id=taxpayer_id,
                    reason="Safety gate triggered",
                    severity="CRITICAL",
                    related_flags=[{"reason": safety_result.get("reason")}],
                    notes="AI-generated content could be unsafe or illegal"
                )
            )

    # -------------------------------------------------
    # Master runner
    # -------------------------------------------------
    def run_escalation(
        self,
        taxpayer_id: str,
        compliance_result: Dict,
        risk_score: Dict,
        safety_result: Dict
    ):
        self.check_compliance(taxpayer_id, compliance_result)
        self.check_risk(taxpayer_id, risk_score)
        self.check_safety(taxpayer_id, safety_result)

        return EscalationResult(
            needs_escalation=bool(self.cases),
            cases=self.cases
        )


# =====================================================
# PUBLIC API FUNCTION
# =====================================================

def evaluate_for_escalation(
    taxpayer_id: str,
    compliance_result: Dict,
    risk_score: Dict,
    safety_result: Dict
) -> EscalationResult:
    """
    Entry point to evaluate a return for human review escalation.
    """
    engine = EscalationEngine()
    return engine.run_escalation(
        taxpayer_id=taxpayer_id,
        compliance_result=compliance_result,
        risk_score=risk_score,
        safety_result=safety_result
    )

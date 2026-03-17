# opportunity_detector.py

from typing import Dict, Any, List


class OpportunityDetector:
    """
    Scans user data and context to identify tax optimization opportunities.
    Produces a list of opportunity objects:
    {
        "type": "unrealized_losses",
        "description": "User has $3,500 in unrealized losses",
        "metadata": {...}
    }
    """

    def detect(self, user: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        opportunities = []

        # Run all detection modules
        opportunities.extend(self._detect_unrealized_losses(user))
        opportunities.extend(self._detect_high_withholding(user))
        opportunities.extend(self._detect_self_employment(user))
        opportunities.extend(self._detect_retirement_gaps(user, context))
        opportunities.extend(self._detect_capital_gains_spike(user))
        opportunities.extend(self._detect_entity_mismatch(user))

        return opportunities

    # -------------------------
    # Detection Modules
    # -------------------------

    def _detect_unrealized_losses(self, user):
        opps = []
        investments = user.get("investments", [])

        losses = [
            a for a in investments
            if a.get("unrealized_losses", 0) > 0
        ]

        if losses:
            total_loss = sum(a["unrealized_losses"] for a in losses)
            opps.append({
                "type": "unrealized_losses",
                "description": f"User has ${total_loss:,} in unrealized losses.",
                "metadata": {"positions": losses}
            })

        return opps

    def _detect_high_withholding(self, user):
        opps = []
        withholding = user.get("withholding", 0)
        tax_liability = user.get("estimated_tax_liability", 0)

        if withholding > tax_liability * 1.25:
            opps.append({
                "type": "over_withholding",
                "description": "User appears to be over-withholding taxes.",
                "metadata": {
                    "withholding": withholding,
                    "estimated_liability": tax_liability
                }
            })

        return opps

    def _detect_self_employment(self, user):
        opps = []
        if user.get("self_employment_income", 0) > 0:
            opps.append({
                "type": "self_employment",
                "description": "Self-employment income detected.",
                "metadata": {
                    "income": user["self_employment_income"]
                }
            })
        return opps

    def _detect_retirement_gaps(self, user, context):
        opps = []
        limits = context.get("irs_limits", {})
        max_401k = limits.get("401k_contribution_limit", 22500)

        contrib = user.get("retirement_contributions", {}).get("401k", 0)

        if contrib < max_401k:
            opps.append({
                "type": "retirement_gap",
                "description": f"User is ${max_401k - contrib:,} below the 401(k) contribution limit.",
                "metadata": {
                    "current_contribution": contrib,
                    "limit": max_401k
                }
            })

        return opps

    def _detect_capital_gains_spike(self, user):
        opps = []
        gains = user.get("capital_gains", 0)

        if gains > 5000:  # threshold can be dynamic later
            opps.append({
                "type": "capital_gains_spike",
                "description": f"User has significant capital gains (${gains:,}).",
                "metadata": {"capital_gains": gains}
            })

        return opps

    def _detect_entity_mismatch(self, user):
        opps = []
        entity = user.get("entity_type")
        income = user.get("net_income", 0)

        if entity == "LLC" and income > 80000:
            opps.append({
                "type": "entity_mismatch",
                "description": "LLC may not be the optimal entity type for this income level.",
                "metadata": {
                    "entity_type": entity,
                    "net_income": income
                }
            })

        return opps

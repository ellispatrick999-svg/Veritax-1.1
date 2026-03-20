from typing import Dict, Any


class SafetyOrchestrator:

    def __init__(self):
        pass

    # 1. INPUT VALIDATION
    def validate_input(self, financial_profile: Dict[str, Any]) -> Dict[str, Any]:

        errors = []

        if not isinstance(financial_profile, dict):
            errors.append("Financial profile must be a dictionary.")

        if "income" in financial_profile and financial_profile["income"] < 0:
            errors.append("Income cannot be negative.")

        if "deductions" in financial_profile:
            if not isinstance(financial_profile["deductions"], dict):
                errors.append("Deductions must be a dictionary.")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    # 2. RULE ENFORCEMENT
    def enforce_rules(self, result: Dict[str, Any]) -> Dict[str, Any]:

        warnings = []

        strategies = result.get("strategies", [])

        for strategy in strategies:
            if strategy.get("estimated_savings", 0) > 100000:
                warnings.append("Unusually high savings detected. Review required.")

        return {
            "safe": True,
            "warnings": warnings
        }

    # 3. MAIN ENTRY POINT
    def process(
        self,
        financial_profile: Dict[str, Any],
        orchestrator
    ) -> Dict[str, Any]:

        # Step 1: Validate input
        validation = self.validate_input(financial_profile)

        if not validation["valid"]:
            return {
                "status": "error",
                "source": "safety_orchestrator",
                "errors": validation["errors"]
            }

        # Step 2: Run core system
        result = orchestrator.run_full_analysis(financial_profile)

        # Step 3: Enforce safety rules
        safety_check = self.enforce_rules(result)

        # Step 4: Return safe output
        return {
            "status": "success",
            "source": "safety_orchestrator",
            "data": result,
            "warnings": safety_check["warnings"]
        }

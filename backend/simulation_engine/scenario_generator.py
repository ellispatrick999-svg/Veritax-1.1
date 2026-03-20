class ScenarioGenerator:

    def generate(self, profile, predictions):
        return {
            "base_income": predictions.get("predicted_income", 0),
            "volatility": predictions.get("income_volatility", 0.1),
            "deductions": profile.get("deductions", 0)
        }

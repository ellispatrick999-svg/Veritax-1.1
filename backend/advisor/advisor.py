from typing import Dict, Any


class Advisor:

    def generate_advice(self, reasoning_output: Dict[str, Any]) -> Dict[str, Any]:

        decision = reasoning_output["data"].get("decision", "")

        if decision == "optimize_tax_strategy":
            message = "You should optimize your tax strategy to reduce liabilities."
        else:
            message = "Your finances look stable."

        return {
            "source": "advisor",
            "data": {
                "advice": message
            },
            "confidence": 0.9
        }


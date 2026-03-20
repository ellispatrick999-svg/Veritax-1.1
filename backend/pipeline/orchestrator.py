from typing import Dict, Any

# Core layers
from prediction.inference_engine import InferenceEngine
from tax_engine.tax_engine import TaxEngine
from strategy_engine.strategy_engine import StrategyEngine
from simulation.simulation_runner import SimulationRunner
from reasoning.reasoning import Reasoning
from advisor.advisor import Advisor

# Safety
from safety.safety_orchestrator import SafetyOrchestrator


class CoreOrchestrator:
    """
    Handles the full AI pipeline WITHOUT safety.
    """

    def __init__(self):
        self.inference_engine = InferenceEngine()
        self.tax_engine = TaxEngine()
        self.strategy_engine = StrategyEngine()
        self.simulation_runner = SimulationRunner()
        self.reasoning = Reasoning()
        self.advisor = Advisor()

    def run_full_analysis(self, financial_profile: Dict[str, Any]) -> Dict[str, Any]:

        # 1️⃣ Prediction
        predictions = self.inference_engine.run(financial_profile)

        # 2️⃣ Tax
        tax = self.tax_engine.calculate(financial_profile)

        # 3️⃣ Strategy
        strategies = self.strategy_engine.generate_strategies(
            financial_profile,
            predictions,
            tax
        )

        # 4️⃣ Simulation
        simulation_results = self.simulation_runner.run(
            financial_profile,
            predictions
        )

        # 5️⃣ Reasoning
        reasoning_output = self.reasoning.analyze(
            financial_profile,
            predictions,
            tax,
            strategies,
            simulation_results
        )

        # 6️⃣ Advisor
        advice = self.advisor.generate_advice(reasoning_output)

        return {
            "status": "success",
            "predictions": predictions,
            "tax": tax,
            "strategies": strategies,
            "simulation": simulation_results,
            "reasoning": reasoning_output,
            "advice": advice
        }


class Orchestrator:
    """
    FINAL ENTRY POINT (includes safety).
    This is what your API should call.
    """

    def __init__(self):
        self.core = CoreOrchestrator()
        self.safety = SafetyOrchestrator()

    def run(self, financial_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Full safe execution pipeline
        """

        return self.safety.process(financial_profile, self.core)

import random
from typing import Dict, List


class MonteCarloEngine:

    def simulate_income(self, base_income: float, volatility: float, runs: int = 1000) -> List[float]:
        results = []

        for _ in range(runs):
            variation = random.uniform(-volatility, volatility)
            simulated_income = base_income * (1 + variation)
            results.append(simulated_income)

        return results

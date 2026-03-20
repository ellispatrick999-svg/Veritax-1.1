class SimulationRunner:

    def __init__(self, monte_carlo_engine):
        self.engine = monte_carlo_engine

    def run(self, scenario):
        incomes = self.engine.simulate_income(
            scenario["base_income"],
            scenario["volatility"]
        )

        return {
            "simulated_incomes": incomes
        }

class ResultAggregator:

    def aggregate(self, results):

        incomes = results["simulated_incomes"]

        return {
            "average_income": sum(incomes) / len(incomes),
            "min_income": min(incomes),
            "max_income": max(incomes)
        }

from copy import deepcopy
from typing import Dict, Any

from exceptions import ScenarioError
from constants import (
    SCENARIO_BASELINE,
    SCENARIO_CONSERVATIVE,
    SCENARIO_AGGRESSIVE
)


class ScenarioEngine:
    def __init__(self, tax_pipeline):
        self.tax_pipeline = tax_pipeline

    def run(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return {
                SCENARIO_BASELINE: self._simulate(user_data, SCENARIO_BASELINE),
                SCENARIO_CONSERVATIVE: self._simulate(user_data, SCENARIO_CONSERVATIVE),
                SCENARIO_AGGRESSIVE: self._simulate(user_data, SCENARIO_AGGRESSIVE),
            }
        except Exception as e:
            raise ScenarioError(str(e)) from e

    def _simulate(self, user_data: Dict[str, Any], mode: str) -> Dict[str, Any]:
        data_copy = deepcopy(user_data)
        data_copy["scenario_mode"] = mode
        return self.tax_pipeline.calculate(data_copy)

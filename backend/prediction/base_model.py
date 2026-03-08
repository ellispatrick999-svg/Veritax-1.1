from abc import ABC, abstractmethod
from typing import Any, Dict


class PredictionModel(ABC):
    """
    Base class for all prediction models.
    Ensures consistent interface across prediction layer.
    """

    @abstractmethod
    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate predictions from input data."""
        pass

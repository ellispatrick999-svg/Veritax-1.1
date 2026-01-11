# safety_profile.py
from typing import Dict, Any
import json

class SafetyProfile:
    """
    Represents a user or system safety profile with risk levels, permissions, and audit settings.
    """

    def __init__(self, user_id: str, risk_level: str = "low", permissions: Dict[str, bool] = None):
        self.user_id = user_id
        self.risk_level = risk_level
        self.permissions = permissions or {}
        self.metadata: Dict[str, Any] = {}

    def set_permission(self, key: str, value: bool) -> None:
        """
        Update a permission flag.
        """
        self.permissions[key] = value

    def update_risk_level(self, level: str) -> None:
        """
        Update the risk level of the profile.
        """
        if level not in {"low", "medium", "high"}:
            raise ValueError("Risk level must be 'low', 'medium', or 'high'.")
        self.risk_level = level

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize profile to dictionary.
        """
        return {
            "user_id": self.user_id,
            "risk_level": self.risk_level,
            "permissions": self.permissions,
            "metadata": self.metadata
        }

    def save_to_json(self, file_path: str) -> None:
        """
        Save profile to JSON file.
        """
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

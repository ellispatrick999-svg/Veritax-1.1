# safety_orchestrator.py
from safety_profile import SafetyProfile
from disclaimer_generator import DisclaimerGenerator
from audit_trail import AuditTrail
from typing import Dict

class SafetyOrchestrator:
    """
    Orchestrates all safety subsystem operations: profiles, disclaimers, and audit logging.
    """

    def __init__(self):
        self.profiles: Dict[str, SafetyProfile] = {}

    def create_profile(self, user_id: str, risk_level: str = "low") -> SafetyProfile:
        """
        Create and store a new safety profile.
        """
        if user_id in self.profiles:
            raise ValueError(f"Profile for {user_id} already exists.")
        profile = SafetyProfile(user_id=user_id, risk_level=risk_level)
        self.profiles[user_id] = profile
        AuditTrail.log_event(user_id, "profile_created", {"risk_level": risk_level})
        return profile

    def update_profile_risk(self, user_id: str, risk_level: str) -> None:
        """
        Update the risk level of a profile.
        """
        profile = self.profiles.get(user_id)
        if not profile:
            raise ValueError(f"No profile found for {user_id}")
        profile.update_risk_level(risk_level)
        AuditTrail.log_event(user_id, "risk_level_updated", {"new_risk_level": risk_level})

    def generate_disclaimer(self, user_id: str, custom_text: str = "") -> str:
        """
        Generate a disclaimer for a specific user and log it.
        """
        if user_id not in self.profiles:
            raise ValueError(f"No profile found for {user_id}")
        disclaimer = DisclaimerGenerator.generate(custom_text)
        AuditTrail.log_event(user_id, "disclaimer_generated", {"disclaimer": disclaimer})
        return disclaimer

    def get_profile(self, user_id: str) -> SafetyProfile:
        """
        Retrieve a safety profile by user ID.
        """
        profile = self.profiles.get(user_id)
        if not profile:
            raise ValueError(f"No profile found for {user_id}")
        return profile

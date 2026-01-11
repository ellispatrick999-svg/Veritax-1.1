# audit_trail.py
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logger
logging.basicConfig(
    filename="audit.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class AuditTrail:
    """
    Logs all safety-related actions and changes for auditing.
    """

    @staticmethod
    def log_event(user_id: str, action: str, details: Dict[str, Any] = None) -> None:
        """
        Log a single audit event.
        """
        details = details or {}
        logging.info(f"User: {user_id} | Action: {action} | Details: {details}")
    
    @staticmethod
    def log_warning(user_id: str, warning: str) -> None:
        """
        Log a warning event.
        """
        logging.warning(f"User: {user_id} | Warning: {warning}")

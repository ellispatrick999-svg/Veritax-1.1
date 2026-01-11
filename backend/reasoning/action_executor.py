"""
action_executor.py

Executes actions derived from reasoning or intent classification.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ActionRequest:
    """Represents an action to perform."""
    type: str  # e.g., "create_reminder", "query_api"
    params: Dict[str, Any]


@dataclass
class ActionResult:
    """Represents the outcome of an action."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class ActionExecutor:
    """
    Central dispatcher for performing side-effectful operations.

    Example actions:
    - Create calendar events
    - Call external APIs
    - Store data in DB

    This layer isolates business logic from reasoning.
    """

    def __init__(self) -> None:
        # Inject external services / clients here.
        pass

    def execute(self, action: ActionRequest) -> ActionResult:
        """
        Dispatch action based on type. Extend with real implementations.
        """
        handler_name = f"_handle_{action.type}"
        handler = getattr(self, handler_name, None)

        if handler is None:
            return ActionResult(
                success=False,
                message=f"Unknown action type: {action.type}",
                data={"requested_action": action.type},
            )

        try:
            return handler(action.params)
        except Exception as exc:  # noqa: BLE001
            return ActionResult(
                success=False,
                message=f"Action '{action.type}' failed: {exc}",
                data={"exception": str(exc)},
            )

    # --------- Example handlers ---------

    def _handle_create_reminder(self, params: Dict[str, Any]) -> ActionResult:
        """
        Example implementation stub for creating a reminder.
        In production, integrate with your task/reminder service.
        """
        # Validate required params
        if "time" not in params or "text" not in params:
            return ActionResult(
                success=False,
                message="Missing required parameters for create_reminder: 'time', 'text'.",
            )

        # TODO: Integrate with real system
        return ActionResult(
            success=True,
            message="Reminder created (stub).",
            data={"time": params["time"], "text": params["text"]},
        )

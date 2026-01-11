"""
dialog_manager.py

Controls multi-turn conversation flow, context management, and stateful
dialog policies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, Optional, List


class DialogState(Enum):
    """High-level states for a conversation."""
    IDLE = auto()
    COLLECTING_INFO = auto()
    EXECUTING_ACTION = auto()
    PROVIDING_EXPLANATION = auto()
    FOLLOW_UP = auto()
    ERROR = auto()


@dataclass
class Turn:
    """Represents one turn in the dialog."""
    role: str  # "user" or "assistant" or "system"
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DialogContext:
    """
    Tracks dialog state and history for a single conversation/session.
    """
    session_id: str
    state: DialogState = DialogState.IDLE
    turns: List[Turn] = field(default_factory=list)
    slots: Dict[str, Any] = field(default_factory=dict)  # for slot-filling/dialog goals


class DialogManager:
    """
    Orchestrates multi-turn dialog.

    Responsibilities:
    - Maintain per-session DialogContext
    - Update state machine based on new user utterances
    - Provide policy decisions (e.g., ask clarification vs. answer vs. act)
    """

    def __init__(self) -> None:
        self._sessions: Dict[str, DialogContext] = {}

    # --------- Session management ---------

    def get_or_create_context(self, session_id: str) -> DialogContext:
        """Return the dialog context for a session, creating it if needed."""
        if session_id not in self._sessions:
            self._sessions[session_id] = DialogContext(session_id=session_id)
        return self._sessions[session_id]

    def reset_context(self, session_id: str) -> None:
        """Clear dialog context for a session."""
        if session_id in self._sessions:
            self._sessions[session_id] = DialogContext(session_id=session_id)

    # --------- Turn handling ---------

    def register_user_turn(self, session_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record a new user turn and update state heuristically."""
        ctx = self.get_or_create_context(session_id)
        ctx.turns.append(Turn(role="user", content=content, metadata=metadata or {}))

        # Simple example policy: always move to COLLECTING_INFO when user speaks
        if ctx.state == DialogState.IDLE:
            ctx.state = DialogState.COLLECTING_INFO

    def register_assistant_turn(
        self,
        session_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        new_state: Optional[DialogState] = None,
    ) -> None:
        """Record assistant's response and optionally update state."""
        ctx = self.get_or_create_context(session_id)
        ctx.turns.append(Turn(role="assistant", content=content, metadata=metadata or {}))
        if new_state is not None:
            ctx.state = new_state

    # --------- Policy decisions ---------

    def should_request_clarification(self, session_id: str, intent_confidence: float) -> bool:
        """
        Simple rule: request clarification if intent confidence is low.
        Tune threshold or make this pluggable.
        """
        return intent_confidence < 0.6

    def mark_error(self, session_id: str, message: str) -> None:
        """Move dialog to ERROR state with an annotation."""
        ctx = self.get_or_create_context(session_id)
        ctx.state = DialogState.ERROR
        ctx.turns.append(
            Turn(role="system", content=f"ERROR: {message}", metadata={"error": True})
        )

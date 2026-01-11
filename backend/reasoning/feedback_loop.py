"""
feedback_loop.py

Collects user feedback on responses and uses it to adjust strategies,
scores, or stored preferences.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class FeedbackItem:
    """
    Represents a piece of feedback from a user about a specific response
    or interaction.
    """
    session_id: str
    turn_id: Optional[int]  # index into dialog history, if applicable
    rating: int  # recommended: 1–5
    comment: Optional[str]
    metadata: Dict[str, Any]


class FeedbackLoop:
    """
    Manages feedback ingestion and exposes signals that other components
    can consume (e.g., to adjust confidence thresholds).
    """

    def __init__(self) -> None:
        self._feedback_items: List[FeedbackItem] = []

    def submit_feedback(self, item: FeedbackItem) -> None:
        """Store a feedback item."""
        if not (1 <= item.rating <= 5):
            raise ValueError("rating must be between 1 and 5.")
        self._feedback_items.append(item)

    def get_all_feedback(self) -> List[FeedbackItem]:
        """Return all collected feedback (for offline analysis)."""
        return list(self._feedback_items)

    def average_rating(self) -> Optional[float]:
        """Compute the global average rating, if any feedback exists."""
        if not self._feedback_items:
            return None
        total = sum(item.rating for item in self._feedback_items)
        return total / len(self._feedback_items)

    def average_rating_for_session(self, session_id: str) -> Optional[float]:
        """Average rating for a specific session."""
        session_items = [f for f in self._feedback_items if f.session_id == session_id]
        if not session_items:
            return None
        total = sum(item.rating for item in session_items)
        return total / len(session_items)

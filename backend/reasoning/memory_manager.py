"""
memory_manager.py

Abstraction over short-term and long-term memory for conversations and
factual storage. Designed to be backend-agnostic (in-memory by default).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class MemoryItem:
    """Represents a single memory entry."""
    id: str
    timestamp: datetime
    type: str  # e.g., "user_message", "fact", "preference"
    content: str
    metadata: Dict[str, Any]


class MemoryManager:
    """
    Manages storage and retrieval of memory.

    Strategies:
    - Short-term: recent conversation turns
    - Long-term: distilled facts, preferences, decisions

    Backend can later be swapped for a database or vector store.
    """

    def __init__(self, max_short_term_items: int = 50) -> None:
        self._short_term: List[MemoryItem] = []
        self._long_term: List[MemoryItem] = []
        self._max_short_term_items = max_short_term_items

    # --------- Insertion ---------

    def add_short_term(self, item: MemoryItem) -> None:
        """Add a short-term memory item, trimming if necessary."""
        self._short_term.append(item)
        if len(self._short_term) > self._max_short_term_items:
            # Drop oldest items
            overflow = len(self._short_term) - self._max_short_term_items
            self._short_term = self._short_term[overflow:]

    def add_long_term(self, item: MemoryItem) -> None:
        """Add a long-term memory item."""
        self._long_term.append(item)

    # --------- Retrieval ---------

    def get_recent_short_term(self, limit: int = 10) -> List[MemoryItem]:
        """Return most recent short-term items, up to limit."""
        if limit <= 0:
            return []
        return self._short_term[-limit:]

    def search_long_term(
        self,
        query: str,
        type_filter: Optional[str] = None,
        limit: int = 20,
    ) -> List[MemoryItem]:
        """
        Naive text search over long-term memory.
        Replace with embedding-based retrieval later.
        """
        query_lower = query.lower()
        candidates = [
            item
            for item in self._long_term
            if query_lower in item.content.lower()
            and (type_filter is None or item.type == type_filter)
        ]
        return candidates[:max(limit, 0)]

    # --------- Utility ---------

    def clear(self) -> None:
        """Clear all memory (useful for tests)."""
        self._short_term.clear()
        self._long_term.clear()

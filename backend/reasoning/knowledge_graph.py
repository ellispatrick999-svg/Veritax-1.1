"""
knowledge_graph.py

Lightweight in-memory knowledge graph abstraction for storing entities,
relations, and attributes, with simple query and reasoning helpers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Iterable


@dataclass(frozen=True)
class Entity:
    """Represents a node in the knowledge graph."""
    id: str
    type: str
    label: Optional[str] = None


@dataclass(frozen=True)
class Relation:
    """Represents a directed edge between two entities."""
    source_id: str
    target_id: str
    type: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class KnowledgeGraph:
    """
    In-memory knowledge graph with basic CRUD and query utilities.

    This is intentionally minimal but structured so you can:
    - Back it with a graph DB later (e.g. Neo4j)
    - Plug it into your inference_engine / reasoner
    """

    def __init__(self) -> None:
        self._entities: Dict[str, Entity] = {}
        self._relations: List[Relation] = []

    # --------- Entity management ---------

    def upsert_entity(self, entity: Entity) -> None:
        """Insert or update an entity."""
        self._entities[entity.id] = entity

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Return an entity by ID."""
        return self._entities.get(entity_id)

    def find_entities_by_type(self, type_name: str) -> List[Entity]:
        """Return all entities of a given type."""
        return [e for e in self._entities.values() if e.type == type_name]

    # --------- Relation management ---------

    def add_relation(self, relation: Relation) -> None:
        """Add a directed relation between two entities."""
        if relation.source_id not in self._entities:
            raise ValueError(f"Unknown source_id: {relation.source_id}")
        if relation.target_id not in self._entities:
            raise ValueError(f"Unknown target_id: {relation.target_id}")
        self._relations.append(relation)

    def get_relations(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        type_name: Optional[str] = None,
    ) -> List[Relation]:
        """
        Query relations by optional source, target, and type.
        All filters are AND-ed together.
        """
        results = self._relations
        if source_id is not None:
            results = [r for r in results if r.source_id == source_id]
        if target_id is not None:
            results = [r for r in results if r.target_id == target_id]
        if type_name is not None:
            results = [r for r in results if r.type == type_name]
        return results

    # --------- Simple reasoning utilities ---------

    def neighbors(self, entity_id: str, relation_type: Optional[str] = None) -> Set[str]:
        """
        Return IDs of neighboring entities reachable from entity_id
        via outgoing relations, optionally filtered by relation type.
        """
        neighbors: Set[str] = set()
        for rel in self._relations:
            if rel.source_id != entity_id:
                continue
            if relation_type is not None and rel.type != relation_type:
                continue
            neighbors.add(rel.target_id)
        return neighbors

    def reachable(
        self,
        start_id: str,
        max_depth: int = 3,
        relation_types: Optional[Iterable[str]] = None,
    ) -> Set[str]:
        """
        Breadth-first traversal returning reachable entity IDs within max_depth.
        Optionally restrict by allowed relation_types.
        """
        if max_depth < 1:
            return set()

        allowed_types = set(relation_types) if relation_types is not None else None
        visited: Set[str] = {start_id}
        frontier: Set[str] = {start_id}

        for _ in range(max_depth):
            next_frontier: Set[str] = set()
            for node_id in frontier:
                for rel in self._relations:
                    if rel.source_id != node_id:
                        continue
                    if allowed_types is not None and rel.type not in allowed_types:
                        continue
                    if rel.target_id not in visited:
                        visited.add(rel.target_id)
                        next_frontier.add(rel.target_id)
            if not next_frontier:
                break
            frontier = next_frontier

        visited.discard(start_id)
        return visited

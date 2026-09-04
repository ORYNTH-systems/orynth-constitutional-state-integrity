from __future__ import annotations

from typing import Any

from .inherited_state import InheritedStateResolver


class LiveInheritedStateResolver:

    def __init__(self):
        self.resolver = InheritedStateResolver()

    def evaluate(
        self,
        historical_state: dict[str, Any],
    ) -> dict[str, Any]:

        dimensions = {
            "source_integrity": historical_state.get(
                "source_integrity",
                "UNRESOLVED",
            ),
            "predicate_integrity": historical_state.get(
                "predicate_integrity",
                "UNRESOLVED",
            ),
            "authority_integrity": historical_state.get(
                "authority_integrity",
                "UNRESOLVED",
            ),
            "jurisdiction_integrity": historical_state.get(
                "jurisdiction_integrity",
                "UNRESOLVED",
            ),
            "evidence_integrity": historical_state.get(
                "evidence_integrity",
                "UNRESOLVED",
            ),
            "transformation_integrity": historical_state.get(
                "transformation_integrity",
                "UNRESOLVED",
            ),
        }

        result = self.resolver.resolve(
            dimensions,
            finality_state=historical_state.get(
                "finality_state",
                "OPEN",
            ),
        )

        return {
            "state_id": historical_state.get("state_id"),
            **result,
        }

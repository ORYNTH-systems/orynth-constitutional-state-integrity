from __future__ import annotations

from typing import Any


class JurisdictionResolver:
    def __init__(self, registry: dict[str, Any]):
        self.registry = registry

    def resolve(self, operation: str, jurisdiction_level: str) -> dict[str, Any]:
        rule = self.registry.get("operations", {}).get(operation)

        if rule is None:
            return {
                "state": "UNRESOLVED",
                "reason": "OPERATION_NOT_REGISTERED",
                "operation": operation,
            }

        allowed = rule.get("allowed_levels", [])

        if jurisdiction_level not in allowed:
            return {
                "state": "INVALID",
                "reason": "JURISDICTION_OUT_OF_SCOPE",
                "operation": operation,
                "jurisdiction_level": jurisdiction_level,
                "allowed_levels": allowed,
            }

        return {
            "state": "VALID",
            "operation": operation,
            "jurisdiction_level": jurisdiction_level,
            "source_anchors": rule.get("source_anchors", []),
        }

from __future__ import annotations

from typing import Any


class AuthorityResolver:
    def __init__(self, registry: dict[str, Any]):
        self.registry = registry

    def resolve(
        self,
        actor_class: str,
        operation: str,
        delegated: bool = False,
        principal_operations: list[str] | None = None,
    ) -> dict[str, Any]:

        actor = self.registry.get("actor_classes", {}).get(actor_class)

        if actor is None:
            return {
                "state": "UNRESOLVED",
                "reason": "ACTOR_CLASS_NOT_REGISTERED",
                "actor_class": actor_class,
            }

        direct_operations = set(actor.get("operations", []))

        if operation in direct_operations:
            return {
                "state": "VALID",
                "basis": "DIRECT",
                "actor_class": actor_class,
                "operation": operation,
            }

        if delegated:
            principal_operations = set(principal_operations or [])

            if operation not in principal_operations:
                return {
                    "state": "INVALID",
                    "reason": "DELEGATION_EXCEEDS_PRINCIPAL",
                    "actor_class": actor_class,
                    "operation": operation,
                }

            return {
                "state": "VALID",
                "basis": "DELEGATED",
                "actor_class": actor_class,
                "operation": operation,
            }

        return {
            "state": "INVALID",
            "reason": "OPERATION_NOT_AUTHORIZED",
            "actor_class": actor_class,
            "operation": operation,
        }

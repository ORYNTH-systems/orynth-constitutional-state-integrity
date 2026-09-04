from __future__ import annotations

from typing import Any


class AuthorityCollisionResolver:

    def resolve(
        self,
        authorities: list[dict[str, Any]],
    ) -> dict[str, Any]:

        active = [
            item
            for item in authorities
            if item.get("state") == "VALID"
        ]

        if not active:
            return {
                "state": "BLOCKED",
                "reason": "NO_VALID_AUTHORITY",
            }

        if len(active) == 1:
            return {
                "state": "NONE",
                "selected": active[0],
            }

        operations = {
            item.get("operation")
            for item in active
        }

        jurisdictions = {
            item.get("jurisdiction")
            for item in active
        }

        authority_sources = {
            item.get("authority_source")
            for item in active
        }

        if len(operations) > 1:
            return {
                "state": "CONFLICTED",
                "reason": "OPERATION_SCOPE_COLLISION",
                "authorities": active,
            }

        if len(jurisdictions) > 1:
            return {
                "state": "CONFLICTED",
                "reason": "JURISDICTION_COLLISION",
                "authorities": active,
            }

        if len(authority_sources) > 1:
            return {
                "state": "CONFLICTED",
                "reason": "SOURCE_SCOPE_COLLISION",
                "authorities": active,
            }

        return {
            "state": "CONFLICTED",
            "reason": "MULTIPLE_UNRESOLVED_VALID_ACTORS",
            "authorities": active,
        }

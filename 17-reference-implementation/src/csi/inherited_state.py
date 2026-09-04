from __future__ import annotations

from typing import Any


class InheritedStateResolver:

    REQUIRED = (
        "source_integrity",
        "predicate_integrity",
        "authority_integrity",
        "jurisdiction_integrity",
        "evidence_integrity",
        "transformation_integrity",
    )

    def resolve(
        self,
        integrity_dimensions: dict[str, str],
        *,
        finality_state: str = "OPEN",
    ) -> dict[str, Any]:

        missing = [
            field
            for field in self.REQUIRED
            if field not in integrity_dimensions
        ]

        if missing:
            return {
                "validation_state": "UNRESOLVED",
                "reason": "MISSING_INTEGRITY_DIMENSIONS",
                "missing": missing,
                "alteration_authorized": False,
            }

        values = {
            integrity_dimensions[field]
            for field in self.REQUIRED
        }

        if "CONFLICTED" in values:
            state = "CONFLICTED"

        elif "INVALID" in values:
            state = "INVALID"

        elif "UNRESOLVED" in values:
            state = "UNRESOLVED"

        elif values == {"VALID"}:
            state = "VALIDATED"

        else:
            state = "UNRESOLVED"

        return {
            "validation_state": state,
            "finality_state": finality_state,
            "alteration_authorized": False,
        }

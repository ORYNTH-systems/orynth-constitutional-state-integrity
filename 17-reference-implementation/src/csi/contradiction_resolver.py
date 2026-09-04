from __future__ import annotations

from typing import Any


class ContradictionResolver:

    def resolve(
        self,
        *,
        source_states: list[str] | None = None,
        predicate_states: list[str] | None = None,
        authority_states: list[str] | None = None,
        jurisdiction_states: list[str] | None = None,
        evidence_states: list[str] | None = None,
        transformation_states: list[str] | None = None,
        state_values: list[str] | None = None,
    ) -> dict[str, Any]:

        groups = {
            "SOURCE_CONTRADICTION": source_states or [],
            "PREDICATE_CONTRADICTION": predicate_states or [],
            "AUTHORITY_CONTRADICTION": authority_states or [],
            "JURISDICTION_CONTRADICTION": jurisdiction_states or [],
            "EVIDENCE_CONTRADICTION": evidence_states or [],
            "TRANSFORMATION_CONTRADICTION": transformation_states or [],
            "STATE_CONTRADICTION": state_values or [],
        }

        contradictions = []

        for contradiction_class, values in groups.items():
            material = {
                value
                for value in values
                if value not in {"INAPPLICABLE", None}
            }

            if "CONFLICTED" in material:
                contradictions.append({
                    "class": contradiction_class,
                    "reason": "EXPLICIT_CONFLICT_STATE",
                })
                continue

            if "VALID" in material and "INVALID" in material:
                contradictions.append({
                    "class": contradiction_class,
                    "reason": "VALID_INVALID_COLLISION",
                })
                continue

            if "TRUE" in material and "FALSE" in material:
                contradictions.append({
                    "class": contradiction_class,
                    "reason": "TRUE_FALSE_COLLISION",
                })

        if contradictions:
            return {
                "state": "CONFLICTED",
                "contradictions": contradictions,
            }

        return {
            "state": "NONE",
            "contradictions": [],
        }

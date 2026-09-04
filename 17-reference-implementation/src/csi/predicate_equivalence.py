from __future__ import annotations

from typing import Any


DIMENSIONS = (
    "subject",
    "condition_set",
    "jurisdiction",
    "temporal_scope",
    "consequence",
)


class PredicateEquivalenceResolver:

    def resolve(
        self,
        left: dict[str, Any],
        right: dict[str, Any],
    ) -> dict[str, Any]:

        missing = [
            dimension
            for dimension in DIMENSIONS
            if dimension not in left or dimension not in right
        ]

        if missing:
            return {
                "relationship": "UNRESOLVED",
                "reason": "MISSING_DIMENSIONS",
                "missing": sorted(set(missing)),
            }

        same = {
            dimension: left[dimension] == right[dimension]
            for dimension in DIMENSIONS
        }

        if all(same.values()):
            return {
                "relationship": "IDENTICAL",
                "dimensions": same,
            }

        left_conditions = set(left.get("condition_set", []))
        right_conditions = set(right.get("condition_set", []))

        structural_dimensions_equal = all(
            same[d]
            for d in (
                "subject",
                "jurisdiction",
                "temporal_scope",
                "consequence",
            )
        )

        if structural_dimensions_equal:

            if left_conditions < right_conditions:
                return {
                    "relationship": "EXPANDED",
                    "dimensions": same,
                }

            if right_conditions < left_conditions:
                return {
                    "relationship": "NARROWED",
                    "dimensions": same,
                }

            if left_conditions & right_conditions:
                return {
                    "relationship": "PARTIALLY_OVERLAPPING",
                    "dimensions": same,
                }

        if left_conditions & right_conditions:
            return {
                "relationship": "PARTIALLY_OVERLAPPING",
                "dimensions": same,
            }

        return {
            "relationship": "DIFFERENT",
            "dimensions": same,
        }

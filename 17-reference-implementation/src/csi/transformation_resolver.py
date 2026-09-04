from __future__ import annotations

from typing import Any


ALLOWED_TYPES = {
    "AMENDMENT",
    "LEGISLATIVE_IMPLEMENTATION",
    "JUDICIAL_INTERPRETATION",
    "EXECUTIVE_APPLICATION",
    "ADMINISTRATIVE_APPLICATION",
    "STATE_APPLICATION",
    "PROCEDURAL_IMPLEMENTATION",
    "SOFTWARE_IMPLEMENTATION",
    "AGENTIC_APPLICATION",
}

ALLOWED_RELATIONSHIPS = {
    "IDENTICAL",
    "NARROWED",
    "EXPANDED",
    "PARTIALLY_OVERLAPPING",
    "DIFFERENT",
    "UNRESOLVED",
}


class TransformationResolver:

    def validate(self, transformation: dict[str, Any]) -> dict[str, Any]:

        required = {
            "transformation_id",
            "source_object",
            "destination_object",
            "transformation_type",
            "authority_class",
            "jurisdiction",
            "predicate_relationship",
            "temporal_scope",
            "provenance",
        }

        missing = sorted(required - transformation.keys())

        if missing:
            return {
                "state": "INVALID",
                "reason": "MISSING_FIELDS",
                "fields": missing,
            }

        if transformation["transformation_type"] not in ALLOWED_TYPES:
            return {
                "state": "INVALID",
                "reason": "UNKNOWN_TRANSFORMATION_TYPE",
            }

        if transformation["predicate_relationship"] not in ALLOWED_RELATIONSHIPS:
            return {
                "state": "INVALID",
                "reason": "UNKNOWN_PREDICATE_RELATIONSHIP",
            }

        if transformation["source_object"] == transformation["destination_object"]:
            return {
                "state": "INVALID",
                "reason": "SOURCE_DESTINATION_COLLAPSE",
            }

        return {
            "state": "VALID",
            "transformation_id": transformation["transformation_id"],
        }

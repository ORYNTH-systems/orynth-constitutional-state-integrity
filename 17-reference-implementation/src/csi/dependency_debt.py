from __future__ import annotations

from typing import Any


class DependencyDebtDetector:

    def detect(self, record: dict[str, Any]) -> dict[str, Any]:

        debts = []

        checks = (
            ("constitutional_source", "MISSING_SOURCE"),
            ("predicate_resolution", "MISSING_PREDICATE"),
            ("authority_resolution", "MISSING_AUTHORITY"),
            ("jurisdiction_resolution", "MISSING_JURISDICTION"),
            ("evidence_resolution", "MISSING_EVIDENCE"),
            ("provenance", "BROKEN_TRANSFORMATION_LINEAGE"),
        )

        for field, debt_class in checks:
            if not record.get(field):
                debts.append({
                    "class": debt_class,
                    "severity": "BLOCKING",
                    "field": field,
                })

        inherited = record.get("inherited_state")

        if inherited:
            state = inherited.get("validation_state")

            if state in {"UNRESOLVED", "CONFLICTED"}:
                debts.append({
                    "class": "UNVERIFIED_INHERITED_STATE",
                    "severity": "BLOCKING",
                    "state": state,
                })

        equivalence = record.get("predicate_equivalence")

        if equivalence:
            relationship = equivalence.get("relationship")

            if relationship == "UNRESOLVED":
                debts.append({
                    "class": "UNRESOLVED_EQUIVALENCE",
                    "severity": "BLOCKING",
                })

        return {
            "debt_count": len(debts),
            "blocking": any(
                debt["severity"] == "BLOCKING"
                for debt in debts
            ),
            "debts": debts,
        }

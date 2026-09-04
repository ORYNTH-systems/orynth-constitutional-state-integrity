from __future__ import annotations


class ConsequenceGate:
    REQUIRED = {
        "source_anchor_status": "VALID",
        "predicate_state": "TRUE",
        "jurisdiction_state": "VALID",
        "authority_state": "VALID",
        "evidence_state": "SUFFICIENT",
    }

    def evaluate(self, state: dict) -> dict:
        conflict_fields = [
            key
            for key, value in state.items()
            if value == "CONFLICTED"
        ]

        if conflict_fields:
            return {
                "result": "CONFLICTED",
                "reason": "MATERIAL_CONFLICT",
                "fields": sorted(conflict_fields),
            }

        failures = []

        for field, expected in self.REQUIRED.items():
            actual = state.get(field)

            if actual != expected:
                failures.append({
                    "field": field,
                    "expected": expected,
                    "actual": actual,
                })

        if failures:
            return {
                "result": "BLOCKED",
                "reason": "CONSEQUENCE_REQUIREMENTS_NOT_SATISFIED",
                "failures": failures,
            }

        return {
            "result": "ADMISSIBLE",
            "reason": "ALL_CONSEQUENCE_REQUIREMENTS_SATISFIED",
        }

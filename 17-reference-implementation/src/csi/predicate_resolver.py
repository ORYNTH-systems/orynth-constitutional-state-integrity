from __future__ import annotations

from typing import Iterable


VALID_STATES = {
    "TRUE",
    "FALSE",
    "UNRESOLVED",
    "CONFLICTED",
    "INAPPLICABLE",
}


def resolve_predicate(
    evidence_states: Iterable[str],
    *,
    protected_constraint_violation: bool = False,
) -> dict:

    states = list(evidence_states)

    if protected_constraint_violation:
        return {
            "state": "CONFLICTED",
            "reason": "PROTECTED_CONSTRAINT_VIOLATION",
        }

    if not states:
        return {
            "state": "UNRESOLVED",
            "reason": "NO_EVIDENCE_STATE",
        }

    unknown = [state for state in states if state not in VALID_STATES]

    if unknown:
        return {
            "state": "UNRESOLVED",
            "reason": "UNKNOWN_EVIDENCE_STATE",
            "values": unknown,
        }

    material = {state for state in states if state != "INAPPLICABLE"}

    if "CONFLICTED" in material:
        return {
            "state": "CONFLICTED",
            "reason": "EVIDENCE_CONFLICT",
        }

    if "UNRESOLVED" in material:
        return {
            "state": "UNRESOLVED",
            "reason": "MATERIAL_EVIDENCE_UNRESOLVED",
        }

    if material == {"TRUE"}:
        return {"state": "TRUE"}

    if material == {"FALSE"}:
        return {"state": "FALSE"}

    if "TRUE" in material and "FALSE" in material:
        return {
            "state": "CONFLICTED",
            "reason": "TRUE_FALSE_CONFLICT",
        }

    if not material:
        return {"state": "INAPPLICABLE"}

    return {
        "state": "UNRESOLVED",
        "reason": "NO_DETERMINATE_RESOLUTION",
    }

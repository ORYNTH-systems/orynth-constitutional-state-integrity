from __future__ import annotations

from typing import Any


class LifecycleError(RuntimeError):
    pass


class LifecycleEngine:

    def __init__(self, transitions: dict[str, set[str]]):
        self.transitions = transitions

    def apply(
        self,
        current_state: str,
        target_state: str,
    ) -> dict[str, Any]:

        allowed = self.transitions.get(
            current_state,
            set(),
        )

        if target_state not in allowed:
            return {
                "state": "BLOCKED",
                "reason": "INVALID_STATE_TRANSITION",
                "current_state": current_state,
                "target_state": target_state,
                "allowed": sorted(allowed),
            }

        return {
            "state": "ADMISSIBLE",
            "prior_state": current_state,
            "new_state": target_state,
        }


def voter_lifecycle() -> LifecycleEngine:
    return LifecycleEngine({
        "PERSON": {"IDENTITY_PENDING"},
        "IDENTITY_PENDING": {"IDENTITY_RESOLVED", "CONFLICTED"},
        "IDENTITY_RESOLVED": {"JURISDICTION_PENDING"},
        "JURISDICTION_PENDING": {"JURISDICTION_RESOLVED", "CONFLICTED"},
        "JURISDICTION_RESOLVED": {"ELIGIBILITY_PENDING"},
        "ELIGIBILITY_PENDING": {
            "ELIGIBLE",
            "INELIGIBLE",
            "CONFLICTED",
        },
        "ELIGIBLE": {"REGISTERED"},
        "REGISTERED": {"BALLOT_PRESENTED"},
        "BALLOT_PRESENTED": {
            "BALLOT_ADMISSIBLE",
            "CONFLICTED",
        },
        "BALLOT_ADMISSIBLE": {"BALLOT_CAST"},
        "BALLOT_CAST": {"TABULATION_ADMISSIBLE"},
        "TABULATION_ADMISSIBLE": {"TABULATED"},
        "TABULATED": {"CANVASSED"},
        "CANVASSED": {"CERTIFIED"},
        "CERTIFIED": {"CHALLENGE_OPEN", "FINAL"},
        "CHALLENGE_OPEN": {"FINAL"},
    })


def citizenship_lifecycle() -> LifecycleEngine:
    return LifecycleEngine({
        "CLAIM_PRESENTED": {"SOURCE_RESOLVED"},
        "SOURCE_RESOLVED": {"FACTS_PENDING"},
        "FACTS_PENDING": {"PREDICATES_PENDING"},
        "PREDICATES_PENDING": {"PREDICATES_RESOLVED"},
        "PREDICATES_RESOLVED": {"DERIVED_AUTHORITY_PENDING"},
        "DERIVED_AUTHORITY_PENDING": {
            "PREDICATE_EQUIVALENCE_PENDING"
        },
        "PREDICATE_EQUIVALENCE_PENDING": {
            "CONSTITUTIONAL_STATE_RESOLVED"
        },
        "CONSTITUTIONAL_STATE_RESOLVED": {
            "INHERITED_STATE_ANALYZED"
        },
        "INHERITED_STATE_ANALYZED": {
            "RELEVANCE_PROPAGATED"
        },
        "RELEVANCE_PROPAGATED": {
            "CONSEQUENCE_AUTHORITY_PENDING"
        },
        "CONSEQUENCE_AUTHORITY_PENDING": {"FINAL"},
    })

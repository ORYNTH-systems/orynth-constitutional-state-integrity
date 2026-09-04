from __future__ import annotations

from collections import defaultdict
from typing import Any


class EvidenceResolver:

    def resolve(
        self,
        evidence: list[dict[str, Any]],
    ) -> dict[str, Any]:

        if not evidence:
            return {
                "state": "UNRESOLVED",
                "reason": "NO_EVIDENCE",
            }

        verified = [
            item
            for item in evidence
            if item.get("integrity_state") == "VERIFIED"
        ]

        conflicted = [
            item
            for item in evidence
            if item.get("integrity_state") == "CONFLICTED"
        ]

        invalid = [
            item
            for item in evidence
            if item.get("integrity_state") == "INVALID"
        ]

        if conflicted:
            return {
                "state": "CONFLICTED",
                "reason": "EXPLICIT_EVIDENCE_CONFLICT",
                "count": len(conflicted),
            }

        claim_values = defaultdict(set)

        for item in verified:
            claim_values[item.get("claim")].add(
                item.get("value")
            )

        contradictory_claims = [
            claim
            for claim, values in claim_values.items()
            if len(values) > 1
        ]

        if contradictory_claims:
            return {
                "state": "CONFLICTED",
                "reason": "VERIFIED_EVIDENCE_DISAGREEMENT",
                "claims": sorted(contradictory_claims),
            }

        if verified:
            return {
                "state": "SUFFICIENT",
                "verified_count": len(verified),
                "invalid_count": len(invalid),
            }

        return {
            "state": "UNRESOLVED",
            "reason": "NO_VERIFIED_EVIDENCE",
            "invalid_count": len(invalid),
        }

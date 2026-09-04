from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


def _canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
    )


def generate_execution_proof(
    *,
    request: dict,
    constitutional_source: dict,
    predicate_resolution: dict,
    jurisdiction_resolution: dict,
    authority_resolution: dict,
    evidence_resolution: dict,
    consequence_resolution: dict,
    deterministic_relevance: dict,
    provenance: dict,
) -> dict[str, Any]:

    body = {
        "request": request,
        "constitutional_source": constitutional_source,
        "predicate_resolution": predicate_resolution,
        "jurisdiction_resolution": jurisdiction_resolution,
        "authority_resolution": authority_resolution,
        "evidence_resolution": evidence_resolution,
        "consequence_resolution": consequence_resolution,
        "deterministic_relevance": deterministic_relevance,
        "provenance": provenance,
    }

    digest = hashlib.sha256(
        _canonical(body).encode("utf-8")
    ).hexdigest().upper()

    return {
        "proof_id": f"CSI.PROOF.{digest[:24]}",
        **body,
        "integrity": {
            "sha256": digest,
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
        },
    }

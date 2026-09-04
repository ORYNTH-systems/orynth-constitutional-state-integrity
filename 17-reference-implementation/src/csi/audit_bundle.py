from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
    )


def generate_audit_bundle(
    *,
    proof_record: dict,
    source_hashes: list[dict],
    dependency_snapshot: dict,
    authority_snapshot: dict,
    evidence_snapshot: dict,
    provenance_snapshot: dict,
    verification_result: dict,
) -> dict:

    payload = {
        "proof_record": proof_record,
        "source_hashes": source_hashes,
        "dependency_snapshot": dependency_snapshot,
        "authority_snapshot": authority_snapshot,
        "evidence_snapshot": evidence_snapshot,
        "provenance_snapshot": provenance_snapshot,
        "verification_result": verification_result,
    }

    digest = hashlib.sha256(
        canonical_json(payload).encode("utf-8")
    ).hexdigest().upper()

    return {
        "bundle_id": f"CSI.AUDIT.{digest[:24]}",
        **payload,
        "integrity": {
            "sha256": digest,
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
        },
    }

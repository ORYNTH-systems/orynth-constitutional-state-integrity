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


def generate_provenance(
    *,
    origin: dict,
    transformations: list[dict],
    current_state: dict,
) -> dict:

    payload = {
        "origin": origin,
        "transformations": transformations,
        "current_state": current_state,
    }

    digest = hashlib.sha256(
        canonical_json(payload).encode("utf-8")
    ).hexdigest().upper()

    return {
        "provenance_id": f"PROV.{digest[:24]}",
        "origin": origin,
        "transformations": transformations,
        "current_state": current_state,
        "integrity": {
            "sha256": digest,
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
        },
    }

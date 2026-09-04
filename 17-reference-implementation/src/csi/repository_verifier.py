from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class RepositoryVerificationFailure(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest().upper()


def verify_repository(repo_root: Path) -> dict[str, Any]:

    required = [
        "BATCH_08_MANIFEST.md",
        "07-constitutional-state-integrity/proof-records/EXECUTION_PROOF_RECORD.schema.json",
        "07-constitutional-state-integrity/contradiction/CONTRADICTION_CONTRACT.json",
        "03-constitutional-dependency-graph/debt/DEPENDENCY_DEBT_CONTRACT.json",
        "08-jurisdiction-and-evidence/audit/AUDIT_BUNDLE.schema.json",
    ]

    missing = [
        item
        for item in required
        if not (repo_root / item).exists()
    ]

    if missing:
        raise RepositoryVerificationFailure(
            f"missing required artifacts: {missing}"
        )

    source_manifest = (
        repo_root
        / "01-constitutional-source-map"
        / "source-integrity"
        / "AUTHORITATIVE_SOURCE_HASHES.json"
    )

    records = json.loads(
        source_manifest.read_text(encoding="utf-8-sig")
    )

    source_results = []

    for record in records:
        path = repo_root / Path(record["path"])

        if not path.exists():
            raise RepositoryVerificationFailure(
                f"missing source: {record['id']}"
            )

        actual = sha256(path)

        if actual != record["sha256"].upper():
            raise RepositoryVerificationFailure(
                f"source mutation: {record['id']}"
            )

        source_results.append({
            "id": record["id"],
            "verified": True,
            "sha256": actual,
        })

    return {
        "repository": "orynth-constitutional-state-integrity",
        "state": "VERIFIED",
        "source_records": source_results,
        "required_artifacts": required,
    }

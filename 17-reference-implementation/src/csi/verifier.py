from __future__ import annotations

import hashlib
import json
from pathlib import Path


class VerificationFailure(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest().upper()


def verify_source_hashes(repo_root: Path) -> list[dict]:
    manifest_path = (
        repo_root
        / "01-constitutional-source-map"
        / "source-integrity"
        / "AUTHORITATIVE_SOURCE_HASHES.json"
    )

    records = json.loads(
        manifest_path.read_text(encoding="utf-8-sig")
    )

    results = []

    for record in records:
        path = repo_root / Path(record["path"])

        if not path.exists():
            raise VerificationFailure(
                f"missing authoritative source: {record['id']}"
            )

        actual = sha256(path)
        expected = record["sha256"].upper()

        if actual != expected:
            raise VerificationFailure(
                f"source hash mismatch: {record['id']}"
            )

        results.append({
            "id": record["id"],
            "sha256": actual,
            "verified": True,
        })

    return results

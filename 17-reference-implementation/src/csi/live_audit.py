from __future__ import annotations

from typing import Any

from .audit_bundle import generate_audit_bundle


class LiveAuditService:

    def create(
        self,
        *,
        execution_response: dict[str, Any],
        source_hashes: list[dict[str, Any]],
        dependency_snapshot: dict[str, Any],
        authority_snapshot: dict[str, Any],
    ) -> dict[str, Any]:

        return generate_audit_bundle(
            proof_record=execution_response["proof_record"],
            source_hashes=source_hashes,
            dependency_snapshot=dependency_snapshot,
            authority_snapshot=authority_snapshot,
            evidence_snapshot=execution_response[
                "evidence_resolution"
            ],
            provenance_snapshot=execution_response[
                "provenance"
            ],
            verification_result={
                "execution_admissible":
                    execution_response[
                        "execution_admissible"
                    ],
                "consequence":
                    execution_response[
                        "consequence_resolution"
                    ],
            },
        )

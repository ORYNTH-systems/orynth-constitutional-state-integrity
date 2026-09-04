from __future__ import annotations

from typing import Any


class FinalityResolver:

    def resolve_reopening(
        self,
        *,
        current_state: str,
        relevance_state: bool,
        authority_state: str,
        jurisdiction_state: str,
        recognized_path: bool,
        evidence_state: str,
    ) -> dict[str, Any]:

        if current_state not in {
            "FINAL",
            "PROVISIONAL",
            "OPEN",
            "REOPENING_REQUESTED",
            "REOPENED",
            "SUPERSEDED",
        }:
            return {
                "result": "REOPEN_CONFLICTED",
                "reason": "UNKNOWN_FINALITY_STATE",
            }

        if current_state == "OPEN":
            return {
                "result": "REOPEN_BLOCKED",
                "reason": "STATE_ALREADY_OPEN",
            }

        if authority_state != "VALID":
            return {
                "result": "REOPEN_BLOCKED",
                "reason": "REOPENING_AUTHORITY_INVALID",
            }

        if jurisdiction_state != "VALID":
            return {
                "result": "REOPEN_BLOCKED",
                "reason": "REOPENING_JURISDICTION_INVALID",
            }

        if not recognized_path:
            return {
                "result": "REOPEN_BLOCKED",
                "reason": "NO_RECOGNIZED_REOPENING_PATH",
            }

        if evidence_state == "CONFLICTED":
            return {
                "result": "REOPEN_CONFLICTED",
                "reason": "EVIDENCE_CONFLICT",
            }

        if relevance_state:
            return {
                "result": "REOPEN_ADMISSIBLE",
                "new_state": "REOPENED",
                "prior_state_preserved": True,
            }

        return {
            "result": "REOPEN_BLOCKED",
            "reason": "NO_REOPENING_BASIS",
        }

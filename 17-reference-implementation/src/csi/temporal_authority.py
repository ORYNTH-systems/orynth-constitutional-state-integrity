from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _parse(value: str) -> datetime:
    parsed = datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


class TemporalAuthorityResolver:

    def resolve(
        self,
        authority: dict[str, Any],
        *,
        at_time: str,
    ) -> dict[str, Any]:

        if authority.get("revoked", False):
            return {
                "state": "REVOKED",
                "execution_valid": False,
            }

        try:
            now = _parse(at_time)
            valid_from = _parse(authority["valid_from"])
            valid_until = _parse(authority["valid_until"])
        except (KeyError, ValueError):
            return {
                "state": "UNRESOLVED",
                "execution_valid": False,
                "reason": "INVALID_TEMPORAL_RECORD",
            }

        if now < valid_from:
            return {
                "state": "NOT_YET_ACTIVE",
                "execution_valid": False,
            }

        if now > valid_until:
            return {
                "state": "EXPIRED",
                "execution_valid": False,
            }

        return {
            "state": "ACTIVE",
            "execution_valid": True,
        }

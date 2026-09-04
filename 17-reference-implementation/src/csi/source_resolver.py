from __future__ import annotations

from typing import Any


class SourceResolver:
    def __init__(self, anchor_registry: dict[str, Any]):
        self.registry = anchor_registry
        self.by_anchor = {
            item["anchor_id"]: item
            for item in anchor_registry.get("anchors", [])
        }

    def resolve(self, anchor_id: str) -> dict[str, Any]:
        item = self.by_anchor.get(anchor_id)

        if item is None:
            return {
                "anchor_id": anchor_id,
                "state": "UNRESOLVED",
                "reason": "ANCHOR_NOT_FOUND",
            }

        if item.get("status") != "VALID":
            return {
                "anchor_id": anchor_id,
                "state": "INVALID",
                "reason": "ANCHOR_NOT_VALID",
            }

        return {
            "anchor_id": anchor_id,
            "state": "VALID",
            "constitutional_unit": item["constitutional_unit"],
            "source_id": item["source_id"],
            "sha256": item["sha256"],
            "locator": item["locator"],
        }

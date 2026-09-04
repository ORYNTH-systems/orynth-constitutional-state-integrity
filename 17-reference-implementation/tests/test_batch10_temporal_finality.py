from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


TEST_FILE = Path(__file__).resolve()
REFERENCE_ROOT = TEST_FILE.parents[1]
REPO_ROOT = REFERENCE_ROOT.parent
SRC_ROOT = REFERENCE_ROOT / "src"

sys.path.insert(0, str(SRC_ROOT))

from csi.authority_collision import AuthorityCollisionResolver
from csi.finality import FinalityResolver
from csi.live_inherited_state import LiveInheritedStateResolver
from csi.temporal_authority import TemporalAuthorityResolver


class Batch10Tests(unittest.TestCase):

    def test_temporal_vectors(self):
        payload = json.loads(
            (
                REFERENCE_ROOT
                / "fixtures"
                / "temporal"
                / "TEMPORAL_AUTHORITY_VECTORS.json"
            ).read_text(encoding="utf-8-sig")
        )

        resolver = TemporalAuthorityResolver()

        for vector in payload["vectors"]:
            with self.subTest(vector=vector["id"]):
                result = resolver.resolve(
                    vector["authority"],
                    at_time=vector["at_time"],
                )

                self.assertEqual(
                    result["state"],
                    vector["expected"],
                )

    def test_collision_vectors(self):
        payload = json.loads(
            (
                REFERENCE_ROOT
                / "fixtures"
                / "collisions"
                / "AUTHORITY_COLLISION_VECTORS.json"
            ).read_text(encoding="utf-8-sig")
        )

        resolver = AuthorityCollisionResolver()

        for vector in payload["vectors"]:
            with self.subTest(vector=vector["id"]):
                result = resolver.resolve(
                    vector["authorities"]
                )

                self.assertEqual(
                    result["state"],
                    vector["expected"],
                )

    def test_finality_vectors(self):
        payload = json.loads(
            (
                REFERENCE_ROOT
                / "fixtures"
                / "finality"
                / "FINALITY_VECTORS.json"
            ).read_text(encoding="utf-8-sig")
        )

        resolver = FinalityResolver()

        for vector in payload["vectors"]:
            with self.subTest(vector=vector["id"]):
                result = resolver.resolve_reopening(
                    **vector["input"]
                )

                self.assertEqual(
                    result["result"],
                    vector["expected"],
                )

    def test_inherited_state_invalid_does_not_authorize_change(self):
        resolver = LiveInheritedStateResolver()

        result = resolver.evaluate({
            "state_id": "HIST-001",
            "source_integrity": "VALID",
            "predicate_integrity": "INVALID",
            "authority_integrity": "VALID",
            "jurisdiction_integrity": "VALID",
            "evidence_integrity": "VALID",
            "transformation_integrity": "VALID",
            "finality_state": "FINAL",
        })

        self.assertEqual(
            result["validation_state"],
            "INVALID",
        )

        self.assertFalse(
            result["alteration_authorized"]
        )

    def test_inherited_final_state_preserves_finality(self):
        resolver = LiveInheritedStateResolver()

        result = resolver.evaluate({
            "state_id": "HIST-002",
            "source_integrity": "VALID",
            "predicate_integrity": "VALID",
            "authority_integrity": "VALID",
            "jurisdiction_integrity": "VALID",
            "evidence_integrity": "VALID",
            "transformation_integrity": "VALID",
            "finality_state": "FINAL",
        })

        self.assertEqual(
            result["validation_state"],
            "VALIDATED",
        )

        self.assertEqual(
            result["finality_state"],
            "FINAL",
        )


if __name__ == "__main__":
    unittest.main()

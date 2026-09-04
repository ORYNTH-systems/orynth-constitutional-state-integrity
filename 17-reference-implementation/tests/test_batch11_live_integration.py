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

from csi.lifecycle import (
    citizenship_lifecycle,
    voter_lifecycle,
)
from csi.live_end_to_end import LiveEndToEndResolver
from csi.registry import RepositoryRegistries


class Batch11Tests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.registries = RepositoryRegistries(
            REPO_ROOT
        )

        source_hashes = json.loads(
            (
                REPO_ROOT
                / "01-constitutional-source-map"
                / "source-integrity"
                / "AUTHORITATIVE_SOURCE_HASHES.json"
            ).read_text(encoding="utf-8-sig")
        )

        cls.resolver = LiveEndToEndResolver(
            source_registry=cls.registries.anchors,
            jurisdiction_registry=cls.registries.jurisdiction,
            authority_registry=cls.registries.authority,
            dependency_graph=cls.registries.graph,
            source_hashes=source_hashes,
        )

    def test_voter_complete_lifecycle(self):
        payload = json.loads(
            (
                REFERENCE_ROOT
                / "fixtures"
                / "lifecycle"
                / "VOTER_COMPLETE_LIFECYCLE.json"
            ).read_text(encoding="utf-8-sig")
        )

        engine = voter_lifecycle()
        state = payload["initial_state"]

        for target in payload["transitions"]:
            result = engine.apply(
                state,
                target,
            )

            self.assertEqual(
                result["state"],
                "ADMISSIBLE",
            )

            state = result["new_state"]

        self.assertEqual(
            state,
            payload["expected_final_state"],
        )

    def test_voter_skip_eligibility_blocks(self):
        payload = json.loads(
            (
                REFERENCE_ROOT
                / "fixtures"
                / "lifecycle"
                / "VOTER_INVALID_TRANSITION.json"
            ).read_text(encoding="utf-8-sig")
        )

        result = voter_lifecycle().apply(
            payload["initial_state"],
            payload["target_state"],
        )

        self.assertEqual(
            result["state"],
            payload["expected"],
        )

    def test_citizenship_complete_lifecycle(self):
        payload = json.loads(
            (
                REFERENCE_ROOT
                / "fixtures"
                / "lifecycle"
                / "CITIZENSHIP_COMPLETE_LIFECYCLE.json"
            ).read_text(encoding="utf-8-sig")
        )

        engine = citizenship_lifecycle()
        state = payload["initial_state"]

        for target in payload["transitions"]:
            result = engine.apply(
                state,
                target,
            )

            self.assertEqual(
                result["state"],
                "ADMISSIBLE",
            )

            state = result["new_state"]

        self.assertEqual(
            state,
            payload["expected_final_state"],
        )

    def test_expired_authority_blocks_live_execution(self):

        result = self.resolver.resolve({
            "request_id": "LIVE-TEMP-001",
            "domain": "VOTER_INTEGRITY",
            "operation": "REMOVE_REGISTRATION",
            "source_anchor": "ANCHOR.CONST.ART1.S2",
            "subject": "SUBJECT-X",
            "jurisdiction_level": "LOCAL",
            "actor_class": "LOCAL_ELECTION_OFFICIAL",
            "execution_time": "2026-09-04T12:00:00Z",
            "predicate_evidence_states": ["TRUE"],
            "evidence": [{
                "integrity_state": "VERIFIED",
                "claim": "eligibility",
                "value": False,
            }],
            "temporal_authority": {
                "valid_from": "2025-01-01T00:00:00Z",
                "valid_until": "2025-12-31T23:59:59Z",
                "revoked": False,
            },
        })

        self.assertFalse(
            result["execution_admissible"]
        )

        self.assertEqual(
            result[
                "temporal_authority_resolution"
            ]["state"],
            "EXPIRED",
        )

    def test_authority_collision_blocks_live_execution(self):

        result = self.resolver.resolve({
            "request_id": "LIVE-COLL-001",
            "domain": "VOTER_INTEGRITY",
            "operation": "CERTIFY",
            "source_anchor": "ANCHOR.CONST.ART1.S4",
            "subject": "ELECTION-X",
            "jurisdiction_level": "STATE",
            "actor_class": "CERTIFICATION_OFFICIAL",
            "execution_time": "2026-09-04T12:00:00Z",
            "predicate_evidence_states": ["TRUE"],
            "evidence": [{
                "integrity_state": "VERIFIED",
                "claim": "canvass_complete",
                "value": True,
            }],
            "competing_authorities": [
                {
                    "state": "VALID",
                    "actor": "OFFICIAL-A",
                    "operation": "CERTIFY",
                    "jurisdiction": "STATE",
                    "authority_source": "SOURCE-A",
                },
                {
                    "state": "VALID",
                    "actor": "OFFICIAL-B",
                    "operation": "CERTIFY",
                    "jurisdiction": "FEDERAL",
                    "authority_source": "SOURCE-B",
                }
            ],
        })

        self.assertFalse(
            result["execution_admissible"]
        )

        self.assertEqual(
            result[
                "authority_collision_resolution"
            ]["state"],
            "CONFLICTED",
        )

    def test_live_audit_bundle_exists_on_block(self):

        result = self.resolver.resolve({
            "request_id": "LIVE-AUDIT-001",
            "domain": "VOTER_INTEGRITY",
            "operation": "REMOVE_REGISTRATION",
            "source_anchor": "ANCHOR.CONST.ART1.S2",
            "subject": "SUBJECT-A",
            "jurisdiction_level": "LOCAL",
            "actor_class": "AUTONOMOUS_AGENT",
            "execution_time": "2026-09-04T12:00:00Z",
            "predicate_evidence_states": ["TRUE"],
            "evidence": [{
                "integrity_state": "VERIFIED",
                "claim": "eligibility",
                "value": False,
            }],
        })

        self.assertFalse(
            result["execution_admissible"]
        )

        self.assertTrue(
            result["audit_bundle"]["bundle_id"].startswith(
                "CSI.AUDIT."
            )
        )


if __name__ == "__main__":
    unittest.main()

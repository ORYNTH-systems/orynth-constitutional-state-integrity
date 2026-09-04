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

from csi.drp import DeterministicRelevanceResolver
from csi.execution_resolver import ExecutionResolver
from csi.predicate_resolver import resolve_predicate
from csi.registry import RepositoryRegistries
from csi.verifier import verify_source_hashes


class CSIKernelTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.registries = RepositoryRegistries(REPO_ROOT)

        cls.execution = ExecutionResolver(
            source_registry=cls.registries.anchors,
            jurisdiction_registry=cls.registries.jurisdiction,
            authority_registry=cls.registries.authority,
        )

        cls.drp = DeterministicRelevanceResolver(
            cls.registries.graph
        )

    def test_authoritative_source_hashes(self):
        results = verify_source_hashes(REPO_ROOT)
        self.assertEqual(len(results), 4)
        self.assertTrue(all(item["verified"] for item in results))

    def test_execution_vectors(self):
        vectors = json.loads(
            (
                REFERENCE_ROOT
                / "fixtures"
                / "EXECUTION_VECTORS.json"
            ).read_text(encoding="utf-8-sig")
        )

        for vector in vectors["vectors"]:
            with self.subTest(vector=vector["id"]):
                result = self.execution.evaluate(**vector["input"])
                self.assertEqual(
                    result["consequence"]["result"],
                    vector["expected"],
                )

    def test_agent_has_no_direct_removal_authority(self):
        result = self.execution.authority.resolve(
            "AUTONOMOUS_AGENT",
            "REMOVE_REGISTRATION",
        )
        self.assertEqual(result["state"], "INVALID")

    def test_delegation_cannot_exceed_principal(self):
        result = self.execution.authority.resolve(
            "AUTONOMOUS_AGENT",
            "REMOVE_REGISTRATION",
            delegated=True,
            principal_operations=["REGISTER"],
        )
        self.assertEqual(result["state"], "INVALID")
        self.assertEqual(
            result["reason"],
            "DELEGATION_EXCEEDS_PRINCIPAL",
        )

    def test_valid_delegation_may_execute_within_principal_scope(self):
        result = self.execution.authority.resolve(
            "AUTONOMOUS_AGENT",
            "REGISTER",
            delegated=True,
            principal_operations=["REGISTER"],
        )
        self.assertEqual(result["state"], "VALID")
        self.assertEqual(result["basis"], "DELEGATED")

    def test_predicate_true(self):
        result = resolve_predicate(["TRUE", "TRUE"])
        self.assertEqual(result["state"], "TRUE")

    def test_predicate_conflict(self):
        result = resolve_predicate(["TRUE", "FALSE"])
        self.assertEqual(result["state"], "CONFLICTED")

    def test_unresolved_predicate_remains_unresolved(self):
        result = resolve_predicate(["TRUE", "UNRESOLVED"])
        self.assertEqual(result["state"], "UNRESOLVED")

    def test_protected_constraint_violation_conflicts(self):
        result = resolve_predicate(
            ["TRUE"],
            protected_constraint_violation=True,
        )
        self.assertEqual(result["state"], "CONFLICTED")

    def test_drp_forward(self):
        result = self.drp.resolve("P.ELIGIBILITY")

        self.assertIn(
            "VIP.REGISTRATION",
            result["prospective_relevance"],
        )

        self.assertIn(
            "VIP.FINALITY",
            result["prospective_relevance"],
        )

        self.assertFalse(result["alteration_authorized"])

    def test_drp_backward(self):
        result = self.drp.resolve("P.ELIGIBILITY")

        self.assertIn(
            "P.VOTER_QUALIFICATION",
            result["retrospective_relevance"],
        )

        self.assertIn(
            "CONST.A14.S1",
            result["retrospective_relevance"],
        )

        self.assertFalse(result["alteration_authorized"])


if __name__ == "__main__":
    unittest.main()

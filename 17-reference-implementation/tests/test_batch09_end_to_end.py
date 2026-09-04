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

from csi.end_to_end import EndToEndResolver
from csi.registry import RepositoryRegistries
from csi.transformation_resolver import TransformationResolver


class Batch09EndToEndTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.registries = RepositoryRegistries(REPO_ROOT)

        cls.resolver = EndToEndResolver(
            source_registry=cls.registries.anchors,
            jurisdiction_registry=cls.registries.jurisdiction,
            authority_registry=cls.registries.authority,
            dependency_graph=cls.registries.graph,
        )

    def test_voter_scenarios(self):
        payload = json.loads(
            (
                REFERENCE_ROOT
                / "fixtures"
                / "scenarios"
                / "VOTER_END_TO_END.json"
            ).read_text(encoding="utf-8-sig")
        )

        for scenario in payload["scenarios"]:
            with self.subTest(scenario=scenario["id"]):
                result = self.resolver.resolve(
                    scenario["request"]
                )

                actual = result[
                    "consequence_resolution"
                ]["result"]

                self.assertEqual(
                    actual,
                    scenario["expected"],
                )

                if actual in {"BLOCKED", "CONFLICTED"}:
                    self.assertFalse(
                        result["execution_admissible"]
                    )

                self.assertIn(
                    "proof_id",
                    result["proof_record"],
                )

                self.assertIn(
                    "provenance_id",
                    result["provenance"],
                )

    def test_citizenship_scenarios(self):
        payload = json.loads(
            (
                REFERENCE_ROOT
                / "fixtures"
                / "scenarios"
                / "CITIZENSHIP_END_TO_END.json"
            ).read_text(encoding="utf-8-sig")
        )

        for scenario in payload["scenarios"]:
            with self.subTest(scenario=scenario["id"]):
                result = self.resolver.resolve(
                    scenario["request"]
                )

                self.assertEqual(
                    result["predicate_equivalence"]["relationship"],
                    scenario["expected_equivalence"],
                )

                if "expected_blocking_debt" in scenario:
                    self.assertEqual(
                        result["dependency_debt"]["blocking"],
                        scenario["expected_blocking_debt"],
                    )

    def test_transformation_scenarios(self):
        payload = json.loads(
            (
                REPO_ROOT
                / "04-authority-lineage"
                / "scenarios"
                / "CONSTITUTIONAL_TRANSFORMATION_SCENARIOS.json"
            ).read_text(encoding="utf-8-sig")
        )

        resolver = TransformationResolver()

        for scenario in payload["scenarios"]:
            with self.subTest(scenario=scenario["id"]):
                expected = scenario.pop("expected")
                scenario.pop("id")

                result = resolver.validate(scenario)

                self.assertEqual(
                    result["state"],
                    expected,
                )


if __name__ == "__main__":
    unittest.main()



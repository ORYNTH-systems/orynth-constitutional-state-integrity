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

from csi.evidence_resolver import EvidenceResolver
from csi.inherited_state import InheritedStateResolver
from csi.predicate_equivalence import PredicateEquivalenceResolver
from csi.provenance import generate_provenance
from csi.transformation_resolver import TransformationResolver


class Batch07Tests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.vectors = json.loads(
            (
                REFERENCE_ROOT
                / "fixtures"
                / "BATCH_07_ADVERSARIAL_VECTORS.json"
            ).read_text(encoding="utf-8-sig")
        )

    def test_predicate_equivalence_vectors(self):
        resolver = PredicateEquivalenceResolver()

        for vector in self.vectors["predicate_equivalence"]:
            with self.subTest(vector=vector["id"]):
                result = resolver.resolve(
                    vector["left"],
                    vector["right"],
                )

                self.assertEqual(
                    result["relationship"],
                    vector["expected"],
                )

    def test_inherited_state_vectors(self):
        resolver = InheritedStateResolver()

        for vector in self.vectors["inherited_state"]:
            with self.subTest(vector=vector["id"]):
                result = resolver.resolve(
                    vector["dimensions"]
                )

                self.assertEqual(
                    result["validation_state"],
                    vector["expected"],
                )

                self.assertFalse(
                    result["alteration_authorized"]
                )

    def test_conflicting_evidence(self):
        resolver = EvidenceResolver()

        result = resolver.resolve([
            {
                "integrity_state": "VERIFIED",
                "claim": "citizenship",
                "value": True,
            },
            {
                "integrity_state": "VERIFIED",
                "claim": "citizenship",
                "value": False,
            },
        ])

        self.assertEqual(
            result["state"],
            "CONFLICTED",
        )

    def test_verified_evidence(self):
        resolver = EvidenceResolver()

        result = resolver.resolve([
            {
                "integrity_state": "VERIFIED",
                "claim": "identity",
                "value": "SUBJECT-1",
            }
        ])

        self.assertEqual(
            result["state"],
            "SUFFICIENT",
        )

    def test_provenance_hash_is_generated(self):
        result = generate_provenance(
            origin={"source": "CONST.A14.S1"},
            transformations=[],
            current_state={"state": "VALID"},
        )

        self.assertTrue(
            result["provenance_id"].startswith("PROV.")
        )

        self.assertEqual(
            len(result["integrity"]["sha256"]),
            64,
        )

    def test_transformation_requires_lineage_fields(self):
        resolver = TransformationResolver()

        result = resolver.validate({
            "transformation_id": "T1"
        })

        self.assertEqual(
            result["state"],
            "INVALID",
        )

    def test_valid_transformation(self):
        resolver = TransformationResolver()

        result = resolver.validate({
            "transformation_id": "T1",
            "source_object": "CONST.A14.S1",
            "destination_object": "CASE.X",
            "transformation_type": "JUDICIAL_INTERPRETATION",
            "authority_class": "JUDICIAL",
            "jurisdiction": "FEDERAL",
            "predicate_relationship": "UNRESOLVED",
            "temporal_scope": "CURRENT",
            "provenance": {"id": "P1"},
        })

        self.assertEqual(
            result["state"],
            "VALID",
        )


if __name__ == "__main__":
    unittest.main()

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

from csi.audit_bundle import generate_audit_bundle
from csi.contradiction_resolver import ContradictionResolver
from csi.dependency_debt import DependencyDebtDetector
from csi.proof_record import generate_execution_proof
from csi.repository_verifier import verify_repository


class Batch08Tests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.vectors = json.loads(
            (
                REFERENCE_ROOT
                / "fixtures"
                / "BATCH_08_ADVERSARIAL_VECTORS.json"
            ).read_text(encoding="utf-8-sig")
        )

    def test_contradiction_vectors(self):
        resolver = ContradictionResolver()

        for vector in self.vectors["contradictions"]:
            kwargs = {
                key: value
                for key, value in vector.items()
                if key.endswith("_states")
            }

            result = resolver.resolve(**kwargs)

            self.assertEqual(
                result["state"],
                vector["expected"],
            )

    def test_dependency_debt_vectors(self):
        detector = DependencyDebtDetector()

        for vector in self.vectors["dependency_debt"]:
            result = detector.detect(vector["record"])

            self.assertEqual(
                result["blocking"],
                vector["blocking"],
            )

    def test_proof_digest_changes_on_request_change(self):
        base = dict(
            constitutional_source={"state":"VALID"},
            predicate_resolution={"state":"TRUE"},
            jurisdiction_resolution={"state":"VALID"},
            authority_resolution={"state":"VALID"},
            evidence_resolution={"state":"SUFFICIENT"},
            consequence_resolution={"result":"ADMISSIBLE"},
            deterministic_relevance={"alteration_authorized":False},
            provenance={"provenance_id":"P1"},
        )

        first = generate_execution_proof(
            request={"operation":"REGISTER"},
            **base,
        )

        second = generate_execution_proof(
            request={"operation":"REMOVE_REGISTRATION"},
            **base,
        )

        self.assertNotEqual(
            first["integrity"]["sha256"],
            second["integrity"]["sha256"],
        )

    def test_audit_bundle_hash_generated(self):
        result = generate_audit_bundle(
            proof_record={"proof_id":"P1"},
            source_hashes=[],
            dependency_snapshot={},
            authority_snapshot={},
            evidence_snapshot={},
            provenance_snapshot={},
            verification_result={"state":"PASS"},
        )

        self.assertTrue(
            result["bundle_id"].startswith("CSI.AUDIT.")
        )

        self.assertEqual(
            len(result["integrity"]["sha256"]),
            64,
        )

    def test_repository_verifier(self):
        result = verify_repository(REPO_ROOT)

        self.assertEqual(
            result["state"],
            "VERIFIED",
        )


if __name__ == "__main__":
    unittest.main()

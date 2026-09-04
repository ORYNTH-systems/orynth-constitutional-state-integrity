from __future__ import annotations

from .contradiction_resolver import ContradictionResolver
from .dependency_debt import DependencyDebtDetector
from .proof_record import generate_execution_proof


class ExecutionAuditor:

    def __init__(self):
        self.contradictions = ContradictionResolver()
        self.debt = DependencyDebtDetector()

    def audit(
        self,
        *,
        request,
        constitutional_source,
        predicate_resolution,
        jurisdiction_resolution,
        authority_resolution,
        evidence_resolution,
        consequence_resolution,
        deterministic_relevance,
        provenance,
        inherited_state=None,
        predicate_equivalence=None,
    ):

        contradiction = self.contradictions.resolve(
            source_states=[
                constitutional_source.get("state")
            ],
            predicate_states=[
                predicate_resolution.get("state")
            ],
            authority_states=[
                authority_resolution.get("state")
            ],
            jurisdiction_states=[
                jurisdiction_resolution.get("state")
            ],
            evidence_states=[
                evidence_resolution.get("state")
            ],
        )

        proof = generate_execution_proof(
            request=request,
            constitutional_source=constitutional_source,
            predicate_resolution=predicate_resolution,
            jurisdiction_resolution=jurisdiction_resolution,
            authority_resolution=authority_resolution,
            evidence_resolution=evidence_resolution,
            consequence_resolution=consequence_resolution,
            deterministic_relevance=deterministic_relevance,
            provenance=provenance,
        )

        debt_input = dict(proof)

        if inherited_state is not None:
            debt_input["inherited_state"] = inherited_state

        if predicate_equivalence is not None:
            debt_input["predicate_equivalence"] = predicate_equivalence

        debt = self.debt.detect(debt_input)

        executable = (
            contradiction["state"] == "NONE"
            and not debt["blocking"]
            and consequence_resolution.get("result")
            == "ADMISSIBLE"
        )

        return {
            "proof_record": proof,
            "contradiction": contradiction,
            "dependency_debt": debt,
            "execution_admissible": executable,
        }

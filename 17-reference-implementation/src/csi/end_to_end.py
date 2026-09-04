from __future__ import annotations

from typing import Any

from .authority_resolver import AuthorityResolver
from .contradiction_resolver import ContradictionResolver
from .consequence_gate import ConsequenceGate
from .dependency_debt import DependencyDebtDetector
from .drp import DeterministicRelevanceResolver
from .evidence_resolver import EvidenceResolver
from .jurisdiction_resolver import JurisdictionResolver
from .predicate_equivalence import PredicateEquivalenceResolver
from .predicate_resolver import resolve_predicate
from .proof_record import generate_execution_proof
from .provenance import generate_provenance
from .source_resolver import SourceResolver


class EndToEndResolver:

    def __init__(
        self,
        *,
        source_registry: dict[str, Any],
        jurisdiction_registry: dict[str, Any],
        authority_registry: dict[str, Any],
        dependency_graph: dict[str, Any],
    ):
        self.source = SourceResolver(source_registry)
        self.jurisdiction = JurisdictionResolver(jurisdiction_registry)
        self.authority = AuthorityResolver(authority_registry)
        self.evidence = EvidenceResolver()
        self.equivalence = PredicateEquivalenceResolver()
        self.drp = DeterministicRelevanceResolver(dependency_graph)
        self.contradiction = ContradictionResolver()
        self.debt = DependencyDebtDetector()
        self.gate = ConsequenceGate()

    def resolve(self, request: dict[str, Any]) -> dict[str, Any]:

        source = self.source.resolve(
            request["source_anchor"]
        )

        evidence = self.evidence.resolve(
            request.get("evidence", [])
        )

        predicate = resolve_predicate(
            request.get(
                "predicate_evidence_states",
                ["UNRESOLVED"],
            ),
            protected_constraint_violation=request.get(
                "protected_constraint_violation",
                False,
            ),
        )

        jurisdiction = self.jurisdiction.resolve(
            request["operation"],
            request["jurisdiction_level"],
        )

        authority = self.authority.resolve(
            request["actor_class"],
            request["operation"],
            delegated=request.get("delegated", False),
            principal_operations=request.get(
                "principal_operations"
            ),
        )

        comparison = None

        if request.get("predicate_comparison"):
            comparison = self.equivalence.resolve(
                request["predicate_comparison"]["left"],
                request["predicate_comparison"]["right"],
            )

        contradiction = self.contradiction.resolve(
            source_states=[source["state"]],
            predicate_states=[predicate["state"]],
            authority_states=[authority["state"]],
            jurisdiction_states=[jurisdiction["state"]],
            evidence_states=[evidence["state"]],
        )

        gate_input = {
            "source_anchor_status": source["state"],
            "predicate_state": predicate["state"],
            "jurisdiction_state": jurisdiction["state"],
            "authority_state": authority["state"],
            "evidence_state": evidence["state"],
        }

        consequence = self.gate.evaluate(
            gate_input
        )

        relevance_node = request.get(
            "relevance_node",
            "P.ELIGIBILITY",
        )

        relevance = self.drp.resolve(
            relevance_node
        )

        provenance = generate_provenance(
            origin={
                "request_id": request["request_id"],
                "source_anchor": request["source_anchor"],
            },
            transformations=[
                {
                    "actor": request["actor_class"],
                    "operation": request["operation"],
                    "input_state": request,
                    "output_state": consequence,
                    "authority_basis": authority,
                }
            ],
            current_state={
                "source": source,
                "predicate": predicate,
                "evidence": evidence,
                "jurisdiction": jurisdiction,
                "authority": authority,
                "consequence": consequence,
            },
        )

        proof = generate_execution_proof(
            request=request,
            constitutional_source=source,
            predicate_resolution=predicate,
            jurisdiction_resolution=jurisdiction,
            authority_resolution=authority,
            evidence_resolution=evidence,
            consequence_resolution=consequence,
            deterministic_relevance=relevance,
            provenance=provenance,
        )

        debt_input = dict(proof)

        if comparison is not None:
            debt_input["predicate_equivalence"] = comparison

        debt = self.debt.detect(
            debt_input
        )

        execution_admissible = (
            contradiction["state"] == "NONE"
            and not debt["blocking"]
            and consequence["result"] == "ADMISSIBLE"
        )

        return {
            "request_id": request["request_id"],
            "source_resolution": source,
            "predicate_resolution": predicate,
            "predicate_equivalence": comparison,
            "evidence_resolution": evidence,
            "jurisdiction_resolution": jurisdiction,
            "authority_resolution": authority,
            "contradiction_resolution": contradiction,
            "dependency_debt": debt,
            "consequence_resolution": consequence,
            "deterministic_relevance": relevance,
            "provenance": provenance,
            "proof_record": proof,
            "execution_admissible": execution_admissible,
        }

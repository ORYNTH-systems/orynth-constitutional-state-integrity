from __future__ import annotations

from typing import Any

from .authority_collision import AuthorityCollisionResolver
from .authority_resolver import AuthorityResolver
from .audit_bundle import generate_audit_bundle
from .contradiction_resolver import ContradictionResolver
from .consequence_gate import ConsequenceGate
from .dependency_debt import DependencyDebtDetector
from .drp import DeterministicRelevanceResolver
from .evidence_resolver import EvidenceResolver
from .finality import FinalityResolver
from .inherited_state import InheritedStateResolver
from .jurisdiction_resolver import JurisdictionResolver
from .predicate_equivalence import PredicateEquivalenceResolver
from .predicate_resolver import resolve_predicate
from .proof_record import generate_execution_proof
from .provenance import generate_provenance
from .source_resolver import SourceResolver
from .temporal_authority import TemporalAuthorityResolver


class LiveEndToEndResolver:

    def __init__(
        self,
        *,
        source_registry: dict[str, Any],
        jurisdiction_registry: dict[str, Any],
        authority_registry: dict[str, Any],
        dependency_graph: dict[str, Any],
        source_hashes: list[dict[str, Any]],
    ):
        self.source = SourceResolver(source_registry)
        self.jurisdiction = JurisdictionResolver(jurisdiction_registry)
        self.authority = AuthorityResolver(authority_registry)
        self.evidence = EvidenceResolver()
        self.equivalence = PredicateEquivalenceResolver()
        self.drp = DeterministicRelevanceResolver(dependency_graph)
        self.contradiction = ContradictionResolver()
        self.debt = DependencyDebtDetector()
        self.temporal = TemporalAuthorityResolver()
        self.collision = AuthorityCollisionResolver()
        self.finality = FinalityResolver()
        self.inherited = InheritedStateResolver()
        self.gate = ConsequenceGate()

        self.dependency_graph = dependency_graph
        self.authority_registry = authority_registry
        self.source_hashes = source_hashes

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

        temporal = {
            "state": "ACTIVE",
            "execution_valid": True,
            "basis": "NO_TEMPORAL_RECORD_REQUIRED",
        }

        if request.get("temporal_authority"):
            temporal = self.temporal.resolve(
                request["temporal_authority"],
                at_time=request["execution_time"],
            )

        competing = request.get(
            "competing_authorities",
            []
        )

        if competing:
            collision = self.collision.resolve(
                competing
            )
        else:
            collision = {
                "state": "NONE",
                "reason": "NO_COMPETING_AUTHORITY",
            }

        comparison = None

        if request.get("predicate_comparison"):
            comparison = self.equivalence.resolve(
                request["predicate_comparison"]["left"],
                request["predicate_comparison"]["right"],
            )

        inherited_state = None

        historical = request.get("historical_state")

        if historical:
            inherited_state = self.inherited.resolve(
                {
                    "source_integrity": historical.get(
                        "source_integrity",
                        "UNRESOLVED",
                    ),
                    "predicate_integrity": historical.get(
                        "predicate_integrity",
                        "UNRESOLVED",
                    ),
                    "authority_integrity": historical.get(
                        "authority_integrity",
                        "UNRESOLVED",
                    ),
                    "jurisdiction_integrity": historical.get(
                        "jurisdiction_integrity",
                        "UNRESOLVED",
                    ),
                    "evidence_integrity": historical.get(
                        "evidence_integrity",
                        "UNRESOLVED",
                    ),
                    "transformation_integrity": historical.get(
                        "transformation_integrity",
                        "UNRESOLVED",
                    ),
                },
                finality_state=historical.get(
                    "finality_state",
                    "OPEN",
                ),
            )

        relevance = self.drp.resolve(
            request.get(
                "relevance_node",
                "P.ELIGIBILITY",
            )
        )

        finality = {
            "result": "NO_REOPENING_REQUEST",
        }

        finality_request = request.get(
            "finality_request"
        )

        if finality_request:
            finality = self.finality.resolve_reopening(
                current_state=finality_request[
                    "current_state"
                ],
                relevance_state=finality_request.get(
                    "relevance_state",
                    bool(
                        relevance.get(
                            "prospective_relevance"
                        )
                        or relevance.get(
                            "retrospective_relevance"
                        )
                    ),
                ),
                authority_state=finality_request[
                    "authority_state"
                ],
                jurisdiction_state=finality_request[
                    "jurisdiction_state"
                ],
                recognized_path=finality_request[
                    "recognized_path"
                ],
                evidence_state=finality_request[
                    "evidence_state"
                ],
            )

        contradiction = self.contradiction.resolve(
            source_states=[source["state"]],
            predicate_states=[predicate["state"]],
            authority_states=[authority["state"]],
            jurisdiction_states=[jurisdiction["state"]],
            evidence_states=[evidence["state"]],
        )

        effective_authority_state = authority["state"]

        if not temporal.get(
            "execution_valid",
            False,
        ):
            effective_authority_state = "INVALID"

        if collision["state"] in {
            "CONFLICTED",
            "BLOCKED",
        }:
            effective_authority_state = "INVALID"

        gate_input = {
            "source_anchor_status": source["state"],
            "predicate_state": predicate["state"],
            "jurisdiction_state": jurisdiction["state"],
            "authority_state": effective_authority_state,
            "evidence_state": evidence["state"],
        }

        consequence = self.gate.evaluate(
            gate_input
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
                    "execution_time":
                        request["execution_time"],
                    "input_state": request,
                    "output_state": consequence,
                    "authority_basis": authority,
                    "temporal_authority": temporal,
                    "authority_collision": collision,
                    "finality": finality,
                }
            ],
            current_state={
                "source": source,
                "predicate": predicate,
                "evidence": evidence,
                "jurisdiction": jurisdiction,
                "authority": authority,
                "temporal_authority": temporal,
                "authority_collision": collision,
                "inherited_state": inherited_state,
                "finality": finality,
                "consequence": consequence,
            },
        )

        proof = generate_execution_proof(
            request=request,
            constitutional_source=source,
            predicate_resolution=predicate,
            jurisdiction_resolution=jurisdiction,
            authority_resolution={
                **authority,
                "temporal": temporal,
                "collision": collision,
            },
            evidence_resolution=evidence,
            consequence_resolution=consequence,
            deterministic_relevance=relevance,
            provenance=provenance,
        )

        debt_input = dict(proof)

        if comparison is not None:
            debt_input["predicate_equivalence"] = comparison

        if inherited_state is not None:
            debt_input["inherited_state"] = inherited_state

        debt = self.debt.detect(
            debt_input
        )

        execution_admissible = (
            contradiction["state"] == "NONE"
            and collision["state"] == "NONE"
            and temporal.get(
                "execution_valid",
                False,
            )
            and not debt["blocking"]
            and consequence["result"] == "ADMISSIBLE"
        )

        audit_bundle = generate_audit_bundle(
            proof_record=proof,
            source_hashes=self.source_hashes,
            dependency_snapshot=self.dependency_graph,
            authority_snapshot=self.authority_registry,
            evidence_snapshot=evidence,
            provenance_snapshot=provenance,
            verification_result={
                "execution_admissible":
                    execution_admissible,
                "consequence":
                    consequence,
                "temporal":
                    temporal,
                "collision":
                    collision,
                "finality":
                    finality,
            },
        )

        return {
            "request_id": request["request_id"],
            "source_resolution": source,
            "predicate_resolution": predicate,
            "predicate_equivalence": comparison,
            "evidence_resolution": evidence,
            "jurisdiction_resolution": jurisdiction,
            "authority_resolution": authority,
            "temporal_authority_resolution": temporal,
            "authority_collision_resolution": collision,
            "inherited_state_resolution": inherited_state,
            "finality_resolution": finality,
            "contradiction_resolution": contradiction,
            "dependency_debt": debt,
            "consequence_resolution": consequence,
            "deterministic_relevance": relevance,
            "provenance": provenance,
            "proof_record": proof,
            "audit_bundle": audit_bundle,
            "execution_admissible": execution_admissible,
        }

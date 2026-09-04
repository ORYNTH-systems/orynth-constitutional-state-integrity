from __future__ import annotations

from .authority_resolver import AuthorityResolver
from .consequence_gate import ConsequenceGate
from .jurisdiction_resolver import JurisdictionResolver
from .source_resolver import SourceResolver


class ExecutionResolver:
    def __init__(
        self,
        *,
        source_registry,
        jurisdiction_registry,
        authority_registry,
    ):
        self.sources = SourceResolver(source_registry)
        self.jurisdiction = JurisdictionResolver(jurisdiction_registry)
        self.authority = AuthorityResolver(authority_registry)
        self.gate = ConsequenceGate()

    def evaluate(
        self,
        *,
        source_anchor,
        operation,
        jurisdiction_level,
        actor_class,
        predicate_state,
        evidence_state,
        delegated=False,
        principal_operations=None,
    ):
        source = self.sources.resolve(source_anchor)

        jurisdiction = self.jurisdiction.resolve(
            operation,
            jurisdiction_level,
        )

        authority = self.authority.resolve(
            actor_class,
            operation,
            delegated=delegated,
            principal_operations=principal_operations,
        )

        gate_input = {
            "source_anchor_status": source["state"],
            "predicate_state": predicate_state,
            "jurisdiction_state": jurisdiction["state"],
            "authority_state": authority["state"],
            "evidence_state": evidence_state,
        }

        gate = self.gate.evaluate(gate_input)

        return {
            "source": source,
            "jurisdiction": jurisdiction,
            "authority": authority,
            "gate_input": gate_input,
            "consequence": gate,
        }

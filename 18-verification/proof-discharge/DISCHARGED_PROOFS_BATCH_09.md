# CSI Discharged Proof Obligations — Batch 09

The following obligations are discharged by executable tests in the current
reference implementation.

## DISCHARGED

CSI-B06-PO-002
Source mutation causes source validation failure before execution.

Evidence:
- source hash verifier
- repository verifier
- source-mutation test gates

CSI-B06-PO-004
Unknown actor classes cannot default to authority.

Evidence:
- AuthorityResolver fail-closed behavior
- kernel tests

CSI-B06-PO-005
Autonomous-agent capability cannot satisfy authority resolution.

Evidence:
- AUTONOMOUS_AGENT has no direct operations
- voter end-to-end removal scenario blocks

CSI-B06-PO-006
Delegated authority cannot exceed principal authority.

Evidence:
- delegation test in test_csi_kernel.py

CSI-B06-PO-007
Unresolved predicates block consequential execution.

Evidence:
- execution vectors
- ConsequenceGate

CSI-B06-PO-008
Conflicting evidence blocks consequential execution.

Evidence:
- evidence resolver
- end-to-end voter conflict scenario

CSI-B06-PO-009
DRP discovers upstream constitutional dependencies.

Evidence:
- DRP backward traversal test

CSI-B06-PO-010
DRP discovers downstream execution dependencies.

Evidence:
- DRP forward traversal test

CSI-B06-PO-011
DRP cannot self-authorize historical alteration.

Evidence:
- alteration_authorized always false in DRP resolver

CSI-B07-PO-003
Predicate identity requires all defined material dimensions.

Evidence:
- PredicateEquivalenceResolver

CSI-B07-PO-004
Narrowed and expanded predicates cannot be labeled identical.

Evidence:
- predicate-equivalence vectors

CSI-B07-PO-005
Evidence disagreement cannot silently resolve into executable state.

Evidence:
- EvidenceResolver conflict behavior

CSI-B07-PO-008
Derived transformations cannot collapse into constitutional source identity.

Evidence:
- TransformationResolver source/destination collapse rejection

CSI-B08-PO-002
Blocked transitions remain reconstructable.

Evidence:
- proof record generated around end-to-end resolution state

CSI-B08-PO-008
Proof digests mutate when request lineage changes.

Evidence:
- Batch 08 proof digest test

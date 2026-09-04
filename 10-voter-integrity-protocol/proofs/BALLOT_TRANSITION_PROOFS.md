# VIP Ballot Transition Proofs

VIP-BAL-PROOF-001

BALLOT_PRESENTED -> BALLOT_ADMISSIBLE requires:

IDENTITY_STATE where required by governing process
AND
ELIGIBILITY_RESOLUTION
AND
JURISDICTION
AND
AUTHORIZED_BALLOT_PROCESS
AND
NO_MATERIAL_UNRESOLVED_CONFLICT

VIP-BAL-PROOF-002

BALLOT_PRESENTED -> REJECTED requires:

EXPLICIT_REJECTION_PREDICATE
AND
SUFFICIENT_EVIDENCE
AND
AUTHORIZED_REJECTION_ACTOR
AND
APPLICABLE_PROCEDURAL_PROTECTION

VIP-BAL-PROOF-003

A system error cannot itself create voter ineligibility.

VIP-BAL-PROOF-004

A software confidence score cannot itself satisfy a constitutional or statutory
eligibility predicate.

VIP-BAL-PROOF-005

Wrongful admission and wrongful rejection are both integrity failures.

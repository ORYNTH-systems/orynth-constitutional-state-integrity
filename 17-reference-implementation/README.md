# CSI Reference Implementation — v0.6

This directory contains the first executable ORYNTH Constitutional State
Integrity kernel.

## Implemented

- constitutional source-anchor resolver
- source-hash verifier
- jurisdiction resolver
- UAA election-authority resolver
- delegation boundary
- constitutional/domain predicate resolver
- deterministic relevance traversal
- consequence gate
- integrated execution resolver
- executable test vectors

## Core execution equation

A consequential state transition is admissible only when:

SOURCE VALID
AND
PREDICATE TRUE
AND
JURISDICTION VALID
AND
AUTHORITY VALID
AND
EVIDENCE SUFFICIENT

## Hard boundaries

- source validity does not create execution authority
- evidence does not create authority
- capability does not create authority
- deterministic relevance does not create alteration authority
- unresolved predicates remain unresolved
- conflicted evidence remains conflicted
- autonomous agents do not self-authorize

## Run verification

From repository root:

python -m unittest discover -s 17-reference-implementation/tests -v

Source-hash CLI:

$env:PYTHONPATH="17-reference-implementation/src"
python -m csi.cli verify-sources

DRP example:

python -m csi.cli drp P.ELIGIBILITY

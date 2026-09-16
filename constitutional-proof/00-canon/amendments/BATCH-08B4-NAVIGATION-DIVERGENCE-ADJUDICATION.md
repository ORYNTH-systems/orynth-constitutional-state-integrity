# BATCH 08B-04 — AMENDMENT TEXT-RANGE ADJUDICATION

amendment_canon_head: 51fb35f30b7d7e02ad690e6bb6a6c3553ae46ae2
pre_crosswalk_baseline: 3a292dbf660893b07da93749bfe80a8de4bba835

## Decision

SEQUENCE A: AUTHORITATIVE CONTENT BODY
SEQUENCE B: PAGE NAVIGATION / EXCLUDED FROM CONSTITUTIONAL TEXT EXTRACTION

## Basis

The Amendments XI-XXVII source capture contains two visible occurrences of each amendment heading.

The first sequence begins at line 370 and ends with Amendment XXVII at line 608.
Those headings are content headings embedded in the amendment body.

The second sequence begins at line 635 after an explicit 'On This Page' heading.
Those entries are href fragment links such as <a href="#xi">AMENDMENT XI</a>.
They constitute navigation/index markup rather than a second constitutional-text rendering.

Sequence B therefore is not an alternative source-text candidate.

## Canonical range policy

Amendments I-X:
- use the unique amendment headings and associated text in the National Archives Bill of Rights transcript capture.

Amendments XI-XXVII:
- use Sequence A authoritative content ranges.
- exclude Sequence B navigation/index markup.

## Extraction boundary

Canonical source ranges may contain:
- amendment heading
- passage/ratification metadata
- National Archives editorial modification/supersession notes
- section labels
- constitutional amendment text

Atomic extraction MUST classify those elements before generating constitutional atoms.

Passage/ratification metadata is provenance metadata, not constitutional operative text.
National Archives editorial notes are source annotations, not constitutional operative text.
Section labels preserve document structure but are not independently substantive clauses.

Only constitutional amendment language may generate constitutional atomic candidates.

## Separations

PAGE NAVIGATION != SOURCE TEXT
EDITORIAL NOTE != CONSTITUTIONAL CLAUSE
RATIFICATION METADATA != OPERATIVE LANGUAGE
SECTION LABEL != ATOMIC MECHANISM
SOURCE != INTERPRETATION
MAPPING != PROOF

## Status

AUTHORITATIVE RANGE SET: 27 / 27
NAVIGATION DIVERGENCE: ADJUDICATED
ATOMIC EXTRACTION: NOT YET PERFORMED

NEXT: BATCH 08B-05 — TEXT SEGMENT CLASSIFICATION / ATOMIC-CANDIDATE GENERATION

# BATCH 02R2 — OBSERVED-LAYOUT EXTRACTION RECOVERY

batch_id: US-CONST-BATCH-02R2
created_utc: 2026-09-11T15:48:10Z
starting_head: 

constitution_sha256:
ADB6D272B6E3D5773CA470D0D53C5CE62396C35FD98469CCC1401DA42099D6EF

candidate_source_units:
24

article_distribution:
- Article I: 10
- Article II: 4
- Article III: 3
- Article IV: 4
- Article V: 1
- Article VI: 1
- Article VII: 1

status:
CANDIDATE-EXTRACTION-RECOVERED

## Observed Parser Failure

The frozen PDF text was intact.

Article IV is extracted as:

Article. I V.

The prior parser assumed an unspaced Roman numeral.

## Recovery Rule

Article headings are identified from exact source lines.

Whitespace inside a Roman numeral is normalized solely
for heading identification.

Source body text is not interpreted by this transformation.

## Evidentiary Boundary

These 24 records are candidate source units.

They are NOT yet canonical constitutional clause boundaries.

No constitutional mechanism has been derived.

No ORYNTH correspondence has been assessed.

## Next Gate

SOURCE VALIDATION
→ CLAUSE BOUNDARY ADJUDICATION
→ VERIFIED-SOURCE

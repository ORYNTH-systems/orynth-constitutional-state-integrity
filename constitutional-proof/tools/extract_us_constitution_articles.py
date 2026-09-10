from pathlib import Path
import csv
import hashlib
import re
import sys

from pypdf import PdfReader

ROOT = Path("constitutional-proof")

PDF = ROOT / "00-canon" / "CONSTITUTION-US.pdf"

RAW_DIR = ROOT / "01-clauses" / "raw-extraction"
RAW_DIR.mkdir(parents=True, exist_ok=True)

REGISTRY = ROOT / "01-clauses" / "CLAUSE-REGISTRY.csv"

REPORT = ROOT / "01-clauses" / "ARTICLE-I-VII-EXTRACTION-REPORT.md"

SOURCE_ID = "US-CONST-SRC-000001"


def normalize_text(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = text.replace("\u00a0", " ")
    text = text.replace("\r", "\n")

    lines = []

    for line in text.splitlines():
        line = re.sub(r"\s+", " ", line).strip()

        if not line:
            lines.append("")
            continue

        lines.append(line)

    out = "\n".join(lines)

    out = re.sub(r"\n{3,}", "\n\n", out)

    return out.strip()


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def sha(text: str) -> str:
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest().upper()


def roman_to_int(value: str) -> int:
    values = {
        "I": 1,
        "II": 2,
        "III": 3,
        "IV": 4,
        "V": 5,
        "VI": 6,
        "VII": 7,
    }
    return values[value.upper()]


reader = PdfReader(str(PDF))

page_text = []

for page_number, page in enumerate(reader.pages, start=1):

    extracted = page.extract_text() or ""

    normalized = normalize_text(extracted)

    page_text.append(
        {
            "page": page_number,
            "text": normalized
        }
    )

    (
        RAW_DIR /
        f"PAGE-{page_number:02d}.txt"
    ).write_text(
        normalized + "\n",
        encoding="utf-8"
    )


full_text = "\n\n".join(
    p["text"] for p in page_text
)

(
    RAW_DIR /
    "CONSTITUTION-EXTRACTED-FULL.txt"
).write_text(
    full_text + "\n",
    encoding="utf-8"
)


# ------------------------------------------------------------
# Locate Article I through Article VII
# ------------------------------------------------------------

article_pattern = re.compile(
    r"(?im)^\s*ARTICLE\.?\s+(I|II|III|IV|V|VI|VII)\.?\s*$"
)

matches = list(article_pattern.finditer(full_text))

if len(matches) < 7:
    # Alternate common extraction form.
    article_pattern = re.compile(
        r"(?im)^\s*ARTICLE\s+(I|II|III|IV|V|VI|VII)\s*$"
    )
    matches = list(article_pattern.finditer(full_text))

found = {}

for m in matches:
    roman = m.group(1).upper()

    if roman not in found:
        found[roman] = m


missing = [
    roman
    for roman in
    ["I","II","III","IV","V","VI","VII"]
    if roman not in found
]

if missing:
    print(
        "ERROR: Missing article headings:",
        ", ".join(missing),
        file=sys.stderr
    )
    sys.exit(20)


ordered = [
    found["I"],
    found["II"],
    found["III"],
    found["IV"],
    found["V"],
    found["VI"],
    found["VII"]
]


article_texts = {}

for index, start_match in enumerate(ordered):

    roman = start_match.group(1).upper()

    start = start_match.start()

    if index + 1 < len(ordered):
        end = ordered[index + 1].start()
    else:
        # Stop before amendments / Bill of Rights if possible.
        tail = full_text[start:]

        amendment_match = re.search(
            r"(?im)^\s*(AMENDMENTS|THE BILL OF RIGHTS)\b",
            tail
        )

        if amendment_match:
            end = start + amendment_match.start()
        else:
            end = len(full_text)

    article = full_text[start:end].strip()

    article_texts[roman] = article

    (
        RAW_DIR /
        f"ARTICLE-{roman}.txt"
    ).write_text(
        article + "\n",
        encoding="utf-8"
    )


# ------------------------------------------------------------
# Candidate section / clause parsing
#
# This intentionally produces CANDIDATE units.
# No row becomes CANONICAL here.
# ------------------------------------------------------------

registry_rows = []

article_counts = {}

for roman, article in article_texts.items():

    article_num = roman_to_int(roman)

    # Remove article heading from body.
    body = article_pattern.sub(
        "",
        article,
        count=1
    ).strip()

    section_pattern = re.compile(
        r"(?im)^\s*SECTION\.?\s+(\d+)\.?\s*$"
    )

    sections = list(section_pattern.finditer(body))

    # Some PDF extractors place "Section. 1." in line text.
    if not sections:
        section_pattern = re.compile(
            r"(?im)^\s*SECTION\.?\s*(\d+)\.?\s*$"
        )
        sections = list(section_pattern.finditer(body))

    article_rows = []

    if sections:

        for section_index, section_match in enumerate(sections):

            section_number = int(section_match.group(1))

            section_start = section_match.end()

            if section_index + 1 < len(sections):
                section_end = sections[section_index + 1].start()
            else:
                section_end = len(body)

            section_body = body[
                section_start:
                section_end
            ].strip()

            # Candidate clause segmentation:
            # paragraph boundaries only.
            candidate_paragraphs = [
                compact(x)
                for x in re.split(
                    r"\n\s*\n",
                    section_body
                )
                if compact(x)
            ]

            if not candidate_paragraphs:
                candidate_paragraphs = [
                    compact(section_body)
                ]

            for clause_number, clause_text in enumerate(
                candidate_paragraphs,
                start=1
            ):

                clause_id = (
                    f"US-CONST-ART{article_num:02d}"
                    f"-SEC{section_number:02d}"
                    f"-CL{clause_number:03d}"
                )

                article_rows.append(
                    {
                        "clause_id": clause_id,
                        "source_id": SOURCE_ID,
                        "article": article_num,
                        "section": section_number,
                        "clause": clause_number,
                        "amendment": "",
                        "source_page": "",
                        "source_locator":
                            f"Article {roman}, "
                            f"Section {section_number}, "
                            f"candidate clause {clause_number}",
                        "original_text": clause_text,
                        "source_text_sha256": sha(clause_text),
                        "supersession_status": "UNASSESSED",
                        "superseded_by": "",
                        "interpretation_status":
                            "CANDIDATE-EXTRACTION"
                    }
                )

    else:
        # Articles IV–VII or extractor layouts may not expose
        # separate section heading lines reliably.
        candidate_paragraphs = [
            compact(x)
            for x in re.split(
                r"\n\s*\n",
                body
            )
            if compact(x)
        ]

        for clause_number, clause_text in enumerate(
            candidate_paragraphs,
            start=1
        ):

            clause_id = (
                f"US-CONST-ART{article_num:02d}"
                f"-SEC00"
                f"-CL{clause_number:03d}"
            )

            article_rows.append(
                {
                    "clause_id": clause_id,
                    "source_id": SOURCE_ID,
                    "article": article_num,
                    "section": 0,
                    "clause": clause_number,
                    "amendment": "",
                    "source_page": "",
                    "source_locator":
                        f"Article {roman}, "
                        f"unresolved section, "
                        f"candidate clause {clause_number}",
                    "original_text": clause_text,
                    "source_text_sha256": sha(clause_text),
                    "supersession_status": "UNASSESSED",
                    "superseded_by": "",
                    "interpretation_status":
                        "CANDIDATE-EXTRACTION"
                }
            )

    article_counts[roman] = len(article_rows)

    registry_rows.extend(article_rows)


if not registry_rows:
    print(
        "ERROR: No candidate constitutional units produced.",
        file=sys.stderr
    )
    sys.exit(21)


fieldnames = [
    "clause_id",
    "source_id",
    "article",
    "section",
    "clause",
    "amendment",
    "source_page",
    "source_locator",
    "original_text",
    "source_text_sha256",
    "supersession_status",
    "superseded_by",
    "interpretation_status",
]


with REGISTRY.open(
    "w",
    newline="",
    encoding="utf-8-sig"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()

    writer.writerows(registry_rows)


# ------------------------------------------------------------
# Extraction report
# ------------------------------------------------------------

report = []

report.append(
    "# ARTICLES I–VII CANDIDATE EXTRACTION REPORT"
)

report.append("")

report.append(
    "status: CANDIDATE-ONLY"
)

report.append(
    "canonical_claim: NOT-YET"
)

report.append(
    "orynth_correspondence_claimed: NO"
)

report.append("")

report.append(
    "## Extracted Candidate Counts"
)

report.append("")

for roman in [
    "I","II","III","IV","V","VI","VII"
]:
    report.append(
        f"- Article {roman}: "
        f"{article_counts.get(roman, 0)} candidate units"
    )

report.append("")

report.append(
    f"TOTAL CANDIDATE UNITS: {len(registry_rows)}"
)

report.append("")

report.append(
    "## Validation Requirement"
)

report.append("")

report.append(
    "Every candidate unit must be checked against the "
    "frozen canonical PDF before interpretation_status "
    "may become VERIFIED-SOURCE."
)

report.append("")

report.append(
    "Paragraph extraction boundaries are not presumed to "
    "equal constitutional legal clause boundaries."
)

report.append("")

report.append(
    "No constitutional mechanism, predicate, ORYNTH binding, "
    "correspondence grade, or proof may be derived from an "
    "unvalidated extraction unit."
)

REPORT.write_text(
    "\n".join(report) + "\n",
    encoding="utf-8"
)


print("")
print("=== EXTRACTION RESULT ===")

for roman in [
    "I","II","III","IV","V","VI","VII"
]:
    print(
        f"ARTICLE {roman}: "
        f"{article_counts.get(roman, 0)} candidate units"
    )

print(
    f"TOTAL: {len(registry_rows)}"
)

print("")
print("STATUS: CANDIDATE-EXTRACTION")
print("CANONICAL: NO")
print("ORYNTH CORRESPONDENCE: NOT ASSESSED")

from pathlib import Path
import csv
import hashlib
import re
import sys

ROOT = Path("constitutional-proof")

RAW = (
    ROOT
    / "01-clauses"
    / "raw-extraction"
    / "CONSTITUTION-EXTRACTED-FULL.txt"
)

REGISTRY = (
    ROOT
    / "01-clauses"
    / "CLAUSE-REGISTRY.csv"
)

REPORT = (
    ROOT
    / "01-clauses"
    / "ARTICLE-I-VII-EXTRACTION-REPORT.md"
)

DIAGNOSTIC = (
    ROOT
    / "01-clauses"
    / "raw-extraction"
    / "ARTICLE-SECTION-DETECTION.txt"
)

SOURCE_ID = "US-CONST-SRC-000001"


def normalize(s: str) -> str:
    s = s.replace("\u00ad", "")
    s = s.replace("\u00a0", " ")
    s = s.replace("\r\n", "\n")
    s = s.replace("\r", "\n")

    lines = []

    for line in s.splitlines():
        line = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(line)

    s = "\n".join(lines)

    s = re.sub(r"\n{3,}", "\n\n", s)

    return s.strip()


def compact(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def sha256_text(s: str) -> str:
    return hashlib.sha256(
        s.encode("utf-8")
    ).hexdigest().upper()


ROMAN = {
    "I": 1,
    "II": 2,
    "III": 3,
    "IV": 4,
    "V": 5,
    "VI": 6,
    "VII": 7,
}


text = normalize(
    RAW.read_text(
        encoding="utf-8",
        errors="replace"
    )
)

# ------------------------------------------------------------
# TOLERANT ARTICLE DETECTION
#
# Supports forms like:
# ARTICLE I
# ARTICLE. I.
# Article I.
# ARTICLE I.
# ARTICLE. I
# ------------------------------------------------------------

article_re = re.compile(
    r"""
    (?imx)
    ^
    \s*
    ARTICLE
    \s*\.?
    \s+
    (VII|VI|IV|V|III|II|I)
    \s*\.?
    \s*
    $
    """
)

article_matches = list(article_re.finditer(text))

# If article headings are not isolated lines, detect them inline.
if len(article_matches) < 7:

    article_re = re.compile(
        r"""
        (?ix)
        \bARTICLE
        \s*\.?
        \s+
        (VII|VI|IV|V|III|II|I)
        \s*\.?
        (?=\s|$)
        """
    )

    article_matches = list(article_re.finditer(text))


found = {}

for match in article_matches:

    roman = match.group(1).upper()

    if roman in ROMAN and roman not in found:
        found[roman] = match


required = [
    "I",
    "II",
    "III",
    "IV",
    "V",
    "VI",
    "VII",
]

missing = [
    roman
    for roman in required
    if roman not in found
]

diagnostic_lines = []

diagnostic_lines.append(
    "=== ARTICLE DETECTION ==="
)

for roman in required:

    if roman in found:
        m = found[roman]

        diagnostic_lines.append(
            f"{roman}: FOUND @ char {m.start()}"
        )
    else:
        diagnostic_lines.append(
            f"{roman}: MISSING"
        )

if missing:

    # dump likely article lines for debugging
    diagnostic_lines.append("")
    diagnostic_lines.append(
        "=== ARTICLE-LIKE RAW LINES ==="
    )

    for i, line in enumerate(
        text.splitlines(),
        start=1
    ):
        if "ARTICLE" in line.upper():
            diagnostic_lines.append(
                f"{i}: {line}"
            )

    DIAGNOSTIC.write_text(
        "\n".join(diagnostic_lines) + "\n",
        encoding="utf-8"
    )

    print(
        "ERROR — missing Articles:",
        ", ".join(missing),
        file=sys.stderr
    )

    sys.exit(30)


# ------------------------------------------------------------
# EXTRACT ARTICLE BLOCKS
# ------------------------------------------------------------

ordered = [
    found[x]
    for x in required
]

articles = {}

for idx, match in enumerate(ordered):

    roman = match.group(1).upper()

    start = match.start()

    if idx + 1 < len(ordered):
        end = ordered[idx + 1].start()
    else:
        tail = text[start:]

        stop_match = re.search(
            r"""
            (?imx)
            ^
            \s*
            (
                AMENDMENTS
                |
                THE\s+BILL\s+OF\s+RIGHTS
                |
                BILL\s+OF\s+RIGHTS
            )
            \b
            """,
            tail
        )

        if stop_match:
            end = start + stop_match.start()
        else:
            end = len(text)

    articles[roman] = text[start:end].strip()


# ------------------------------------------------------------
# TOLERANT SECTION DETECTION
#
# Supports:
# Section 1.
# SECTION. 1.
# Sec. 1.
# Section.1.
# ------------------------------------------------------------

section_re = re.compile(
    r"""
    (?imx)
    ^
    \s*
    (
        SECTION
        |
        SEC
    )
    \s*\.?
    \s*
    (\d+)
    \s*\.?
    \s*
    $
    """
)


rows = []
article_counts = {}

for roman in required:

    article_num = ROMAN[roman]

    block = articles[roman]

    # Remove heading itself.
    heading_re = re.compile(
        rf"""
        (?ix)
        \bARTICLE
        \s*\.?
        \s+
        {roman}
        \s*\.?
        """
    )

    body = heading_re.sub(
        "",
        block,
        count=1
    ).strip()

    section_matches = list(
        section_re.finditer(body)
    )

    # fallback: sections not isolated on own line
    if not section_matches:

        inline_section_re = re.compile(
            r"""
            (?ix)
            \b
            (
                SECTION
                |
                SEC
            )
            \s*\.?
            \s*
            (\d+)
            \s*\.?
            """
        )

        section_matches = list(
            inline_section_re.finditer(body)
        )

        active_section_re = inline_section_re

    else:
        active_section_re = section_re

    article_rows = []

    # --------------------------------------------------------
    # If sections detected, parse section bodies.
    # --------------------------------------------------------

    if section_matches:

        for sidx, sm in enumerate(section_matches):

            section_num = int(
                sm.group(2)
            )

            start = sm.end()

            if sidx + 1 < len(section_matches):
                end = section_matches[
                    sidx + 1
                ].start()
            else:
                end = len(body)

            section_body = body[
                start:end
            ].strip()

            # First try blank-line paragraph boundaries.
            paragraphs = [
                compact(x)
                for x in re.split(
                    r"\n\s*\n",
                    section_body
                )
                if compact(x)
            ]

            # If extraction collapsed all paragraphs,
            # preserve entire section as one candidate unit.
            if not paragraphs and compact(section_body):

                paragraphs = [
                    compact(section_body)
                ]

            for idx, paragraph in enumerate(
                paragraphs,
                start=1
            ):

                article_rows.append(
                    {
                        "clause_id":
                            f"US-CONST-ART{article_num:02d}"
                            f"-SEC{section_num:02d}"
                            f"-CL{idx:03d}",

                        "source_id":
                            SOURCE_ID,

                        "article":
                            article_num,

                        "section":
                            section_num,

                        "clause":
                            idx,

                        "amendment":
                            "",

                        "source_page":
                            "",

                        "source_locator":
                            f"Article {roman}, "
                            f"Section {section_num}, "
                            f"candidate unit {idx}",

                        "original_text":
                            paragraph,

                        "source_text_sha256":
                            sha256_text(paragraph),

                        "supersession_status":
                            "UNASSESSED",

                        "superseded_by":
                            "",

                        "interpretation_status":
                            "CANDIDATE-EXTRACTION",
                    }
                )

    # --------------------------------------------------------
    # Articles without reliably detected sections
    # get article-level candidate paragraph units.
    # --------------------------------------------------------

    else:

        paragraphs = [
            compact(x)
            for x in re.split(
                r"\n\s*\n",
                body
            )
            if compact(x)
        ]

        if not paragraphs and compact(body):
            paragraphs = [
                compact(body)
            ]

        for idx, paragraph in enumerate(
            paragraphs,
            start=1
        ):

            article_rows.append(
                {
                    "clause_id":
                        f"US-CONST-ART{article_num:02d}"
                        f"-SEC00"
                        f"-CL{idx:03d}",

                    "source_id":
                        SOURCE_ID,

                    "article":
                        article_num,

                    "section":
                        0,

                    "clause":
                        idx,

                    "amendment":
                        "",

                    "source_page":
                        "",

                    "source_locator":
                        f"Article {roman}, "
                        f"unresolved section, "
                        f"candidate unit {idx}",

                    "original_text":
                        paragraph,

                    "source_text_sha256":
                        sha256_text(paragraph),

                    "supersession_status":
                        "UNASSESSED",

                    "superseded_by":
                        "",

                    "interpretation_status":
                        "CANDIDATE-EXTRACTION",
                }
            )

    article_counts[roman] = len(
        article_rows
    )

    rows.extend(
        article_rows
    )


# ------------------------------------------------------------
# HARD VALIDATION
# ------------------------------------------------------------

if len(rows) == 0:
    print(
        "ERROR — parser produced 0 units.",
        file=sys.stderr
    )
    sys.exit(31)


missing_articles = [
    roman
    for roman in required
    if article_counts.get(
        roman,
        0
    ) == 0
]

if missing_articles:
    print(
        "ERROR — zero candidate units in Articles:",
        ", ".join(missing_articles),
        file=sys.stderr
    )
    sys.exit(32)


ids = [
    row["clause_id"]
    for row in rows
]

if len(ids) != len(set(ids)):
    print(
        "ERROR — duplicate clause IDs.",
        file=sys.stderr
    )
    sys.exit(33)


for row in rows:

    if not row["source_text_sha256"]:
        print(
            "ERROR — missing SHA.",
            file=sys.stderr
        )
        sys.exit(34)

    if not row["original_text"]:
        print(
            "ERROR — empty source unit.",
            file=sys.stderr
        )
        sys.exit(35)


# ------------------------------------------------------------
# WRITE REGISTRY
# ------------------------------------------------------------

fields = [
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
) as handle:

    writer = csv.DictWriter(
        handle,
        fieldnames=fields
    )

    writer.writeheader()

    writer.writerows(
        rows
    )


# ------------------------------------------------------------
# WRITE DIAGNOSTIC
# ------------------------------------------------------------

diagnostic_lines.append("")
diagnostic_lines.append(
    "=== CANDIDATE COUNTS ==="
)

for roman in required:

    diagnostic_lines.append(
        f"ARTICLE {roman}: "
        f"{article_counts[roman]}"
    )

diagnostic_lines.append(
    f"TOTAL: {len(rows)}"
)

DIAGNOSTIC.write_text(
    "\n".join(
        diagnostic_lines
    ) + "\n",
    encoding="utf-8"
)


# ------------------------------------------------------------
# WRITE REPORT
# ------------------------------------------------------------

report = []

report.append(
    "# ARTICLES I–VII EXTRACTION RECOVERY REPORT"
)

report.append("")
report.append(
    "status: CANDIDATE-EXTRACTION-RECOVERED"
)
report.append(
    "canonical_claim: NO"
)
report.append(
    "orynth_correspondence_claimed: NO"
)
report.append("")

report.append(
    "## Candidate Counts"
)
report.append("")

for roman in required:

    report.append(
        f"- Article {roman}: "
        f"{article_counts[roman]}"
    )

report.append("")

report.append(
    f"TOTAL CANDIDATE UNITS: {len(rows)}"
)

report.append("")

report.append(
    "## Evidentiary Boundary"
)

report.append("")

report.append(
    "These are extraction candidates only."
)

report.append(
    "They are not yet verified constitutional clause boundaries."
)

report.append(
    "No mechanism normalization or ORYNTH correspondence "
    "may rely on these rows until source validation is complete."
)

REPORT.write_text(
    "\n".join(report) + "\n",
    encoding="utf-8"
)


print("")
print("=== BATCH 02R EXTRACTION RESULT ===")

for roman in required:
    print(
        f"ARTICLE {roman}: "
        f"{article_counts[roman]}"
    )

print(
    f"TOTAL CANDIDATE UNITS: {len(rows)}"
)

print("")
print(
    "STATUS: CANDIDATE-EXTRACTION-RECOVERED"
)

print(
    "CANONICAL: NO"
)

print(
    "ORYNTH CORRESPONDENCE: NOT ASSESSED"
)

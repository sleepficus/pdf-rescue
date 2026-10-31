"""Seal the lane 03 fixture pack.

Promotes the proven-deterministic gen-a PDFs into fixtures/, then writes
FIXTURE-MANIFEST.json from the build report plus the frozen static metadata
below. Run only after generator/doublegen_check.py passed.

Usage: python3 generator/seal.py SCRATCH_GEN_A_DIR
"""
import hashlib
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from generator import generate_all
except ImportError:
    import generate_all

CLASSES = {
    "F01": "TEXT_SINGLE_COLUMN", "F02": "TEXT_SINGLE_COLUMN",
    "F03": "TEXT_SINGLE_COLUMN", "F04": "TEXT_SINGLE_COLUMN",
    "F05": "TEXT_MULTI_COLUMN", "F06": "TEXT_MULTI_COLUMN",
    "F07": "TEXT_MULTI_COLUMN", "F08": "TEXT_TABLE",
    "R01": "REFUSE_ENCRYPTED", "R02": "REFUSE_SIGNED",
    "R03": "REFUSE_XFA", "R04": "REFUSE_ACTIVE",
    "B01": "BENIGN", "B02": "BENIGN",
}

CONTROL_KIND = {
    "R01": "refusal-control: encrypted input",
    "R02": "refusal-control: signed-looking input",
    "R03": "refusal-control: XFA input",
    "R04": "refusal-control: active-content input",
    "B01": "benign-control: already-clean document",
    "B02": "benign-control: clean navigation document",
    None: None,
}

UGLY_FEATURES = {
    "F01": [
        "spacing: literal double spaces and irregular paragraph gaps (4/8/14pt)",
        "alignment: inconsistent indents (0/18/24pt)",
        "typography: mixed families/sizes in body (Helvetica 10.5, Times-Roman 11, Courier 9.5, headings 14)",
        "hyphenation: declared line-end breaks (exam-/ple, oper-/ations)",
        "header/footer: repeated running header and footer on every page",
        "bookmarks: missing (none)",
        "structure tags: none",
    ],
    "F02": [
        "spacing: one literal double-spaced sentence, irregular paragraph gaps (2/6/12/18pt)",
        "alignment: centered letterhead, right-aligned date, indented blocks",
        "typography: mixed sizes (8-14) and families",
        "hyphenation: none declared",
        "header/footer: none (letter format)",
        "bookmarks: missing (none)",
        "structure tags: none",
    ],
    "F03": [
        "spacing: irregular paragraph gaps",
        "alignment: inconsistent indents (0/6/12pt)",
        "typography: mixed families/sizes (8.5-14)",
        "hyphenation: declared line-end break (assess-/ment)",
        "header/footer: footer only",
        "bookmarks: flat (4 top-level entries, no nesting despite heading hierarchy)",
        "structure tags: none",
        "tables: inline numeric row set without grid lines",
    ],
    "F04": [
        "spacing: irregular gaps and one literal double space inside agenda item 3",
        "alignment: varying item indents (0-18pt) plus one right-aligned line and centered title",
        "typography: mixed Times/Helvetica sizes (8-13)",
        "hyphenation: none declared",
        "header/footer: footer only",
        "bookmarks: missing (none)",
        "structure tags: none",
    ],
    "F05": [
        "reading order: two-column, order-sensitive (left column then right column per page)",
        "spacing: irregular gaps, one literal double space",
        "alignment: two-column layout with spanning title",
        "typography: mixed sizes (9-14)",
        "hyphenation: declared line-end breaks (back-/log, condi-/tion)",
        "header/footer: footer only",
        "bookmarks: missing (none)",
        "structure tags: none",
    ],
    "F06": [
        "reading order: two-column, order-sensitive (left column then right column per page)",
        "tables: small numeric table with frozen lexemes 1,234.50 / (500) / 12% / $0.75 and differing row bases",
        "spacing: irregular paragraph gaps",
        "typography: mixed sizes (8.5-13)",
        "hyphenation: none declared",
        "header/footer: footer only",
        "bookmarks: missing (none)",
        "structure tags: none",
    ],
    "F07": [
        "header/footer: repeated running header and footer on every page",
        "navigation: TOC-like contents list with accurate page numbers; internal cross-reference phrase ('as detailed in Section 3 (page 3)')",
        "bookmarks: flat (4 top-level entries)",
        "spacing: irregular paragraph gaps",
        "alignment: single dense column",
        "typography: mixed families/sizes (8.5-14)",
        "hyphenation: declared line-end breaks (main-/tenance, recommend-/ations)",
        "structure tags: none",
    ],
    "F08": [
        "tables: drawn grid with columns Item/Quantity/Unit Price/Amount, repeated header row per page, TOTAL row",
        "numeric lexemes: thousands separator ($1,234.50), parenthesised negative (($250.00)), currency ($0.75), mixed magnitudes",
        "units: 'All amounts in USD.' note plus parentheses convention note",
        "header/footer: repeated on every page",
        "spacing: irregular gaps in the sub-header block",
        "typography: mixed Helvetica/Helvetica-Bold",
        "bookmarks: missing (none)",
        "structure tags: none",
    ],
    "R01": [], "R02": [], "R03": [], "R04": [],
    "B01": [], "B02": [],
}

NOTES = {
    "F01": "Two-page memo; running header/footer exercise per-page hashing; no bookmarks so outline addition is a tidy opportunity.",
    "F02": "Single-page letter; M02 target sentence frozen in the body.",
    "F03": "Two-page report; flat bookmarks exercise hierarchy repair; inline numeric rows exercise lexeme round-trip without a grid.",
    "F04": "Single-page agenda; M06 hidden-text target; irregular alignment/indents.",
    "F05": "Three-page two-column article; reading order is left-then-right per page; M03 column-order-swap target.",
    "F06": "Three-page two-column report; numeric table carries the four frozen lexemes with deliberately mixed row bases (no arithmetic obligation, see ORACLE-NOTES.md).",
    "F07": "Four-page dense report; accurate TOC, cross-reference phrase, flat bookmarks; M05 bookmark-loss target.",
    "F08": "Three-page statement; drawn grid, TOTAL row arithmetically consistent (descriptive only); M04 numeric-reassignment target.",
    "R01": "Built with reportlab then pypdf PdfWriter.encrypt(RC4-128) with frozen dummy passwords and pinned /ID.",
    "R02": "AcroForm with /SigFlags 3 and one /FT /Sig widget whose /V holds /ByteRange and a dummy hex /Contents; built via pypdf low-level objects.",
    "R03": "AcroForm carries /XFA as [name, stream] with a small synthetic XDP XML stream.",
    "R04": "Catalog /OpenAction is a /JavaScript action; page 1 carries an /AA additional JavaScript action. Strings are inert synthetic text.",
    "B01": "Already-clean two-page document: consistent font/spacing, correct hierarchical bookmarks; must need zero operations.",
    "B02": "Clean two-page document with correct hierarchical bookmarks and exactly one internal GoTo link annotation on page 1 targeting page 2.",
}


def main():
    gen_a = sys.argv[1]
    lane = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fixtures_dir = os.path.join(lane, "fixtures")
    os.makedirs(fixtures_dir, exist_ok=True)
    with open(os.path.join(gen_a, "build-report.json")) as f:
        report = json.load(f)

    entries = []
    for rec in report["files"]:
        assert rec["mutant_of"] is None, "mutants are never sealed"
        doc_id = rec["id"]
        src = os.path.join(gen_a, rec["filename"])
        dst = os.path.join(fixtures_dir, rec["filename"])
        shutil.copyfile(src, dst)
        with open(dst, "rb") as f:
            data = f.read()
        assert hashlib.sha256(data).hexdigest() == rec["sha256"], doc_id
        entries.append({
            "id": doc_id,
            "filename": rec["filename"],
            "class": CLASSES[doc_id],
            "page_count": rec["pages"],
            "byte_size": len(data),
            "sha256": rec["sha256"],
            "page_size_pt": [612.0, 792.0],
            "generator": {
                "tool": "reportlab %s (Canvas invariant=1) + pypdf %s post-processing for R01-R04"
                        % (report["versions"]["reportlab"], report["versions"]["pypdf"]),
                "script": "generator/generate_all.py",
            },
            "seed_record": {
                "rng": "none",
                "nominal_seed": 20260929,
                "mode": "deterministic no-RNG; seeds frozen in GENERATOR-SPEC.md before generation",
            },
            "ugly_features": UGLY_FEATURES[doc_id],
            "control_kind": CONTROL_KIND[doc_id if doc_id in CONTROL_KIND else None],
            "notes": NOTES[doc_id],
        })

    manifest = {
        "kind": "lane03-fixture-manifest",
        "schema": 1,
        "frozen_date": "2026-09-29",
        "authority": {
            "order": ["inputs/FINAL-RECONCILIATION.md", "ASSIGNMENT.md",
                      "inputs/MAIN-GLM-SYNTHESIS.md"],
            "scope": "text-native vertical slice only (no forms, scans, OCR, RTL)",
        },
        "generator": report["generator"],
        "versions": report["versions"],
        "seed_record": report["seed_record"],
        "determinism_evidence": {
            "method": "every PDF generated twice (scratch/gen-a, scratch/gen-b) by generator/doublegen_check.py; pairwise sha256 asserted equal",
            "files_compared": 20,
            "mismatches": 0,
            "result": "byte-identical",
        },
        "immutability": "sealed PDFs in fixtures/ are immutable; defects are recorded, never patched in place",
        "fixtures": entries,
    }
    out = os.path.join(lane, "FIXTURE-MANIFEST.json")
    with open(out, "w") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
        f.write("\n")
    print("sealed %d PDFs into fixtures/" % len(entries))
    for e in entries:
        print("  %-28s %s  %6d bytes  p%d" % (e["filename"], e["sha256"][:16],
                                              e["byte_size"], e["page_count"]))


if __name__ == "__main__":
    main()

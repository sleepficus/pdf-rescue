# Wave B compact frozen reference

This is a lossless implementation reference for the vertical slice. The full
Gate A artifacts remain authoritative with Main; this packet intentionally
contains only the frozen facts needed to write the named modules.

## Classes and intake precedence

Refusal scan order is `REFUSE_ENCRYPTED`, `REFUSE_SIGNED`, `REFUSE_XFA`,
`REFUSE_ACTIVE`. Detect `/Encrypt`; signatures via `/Sig`, `/DocMDP`, `/Perms`
or `/ByteRange`; `/XFA`; and active/pending-redaction constructs
`/JavaScript`, `/JS`, `/Launch`, `/EmbeddedFile`, `/GoToR`, `/GoToE`,
`/OpenAction`, `/Redact`. A refusal happens before extraction, creates no
candidate, and records gates `NOT_EXERCISED`.

After a clean refusal scan: parse/classifier failure -> `UNRESOLVED`; a table
with at least 2x2 cells sharing at least three x and y boundaries within 2pt
and adjacent gaps under 36pt -> `TEXT_TABLE`; otherwise stable separated
columns -> `TEXT_MULTI_COLUMN`; otherwise `TEXT_SINGLE_COLUMN`, or `BENIGN`
when `plan.operations == []`. Never guess an uncertain class.

## Frozen operations and expected deltas

Allowed operations:

`OP_SPACING_NORMALIZE`, `OP_ALIGNMENT_NORMALIZE`,
`OP_TYPOGRAPHY_SUBSTITUTION`, `OP_HYPHENATION_JOIN`,
`OP_HEADER_FOOTER_NORMALIZATION`, `OP_STRUCTURE_TAGS`, `OP_READING_ORDER`,
`OP_BOOKMARKS`, `OP_LINK_REPAIR`, `OP_PAGE_ROTATE`.

Allowed delta types:

`SPACING_COLLAPSE`, `LINE_END_WHITESPACE_STRIP`, `ALIGNMENT_SHIFT`,
`GLYPH_SUBSTITUTION`, `HYPHENATION_JOIN`,
`HEADER_FOOTER_INSTANCE_NORMALIZATION`, `STRUCTURE_TAG_ADD`,
`READING_ORDER_SET`, `BOOKMARK_ADD`, `BOOKMARK_DEST_REPAIR`,
`LINK_DEST_REPAIR`, `PAGE_ROTATE_REVIEW`.

Every operation declares stable page/element/region anchors and one expected
delta with page/element scope plus `max_affected_tokens`,
`max_affected_regions`, and `max_affected_area_fraction`. No operation may
change a numeric lexeme. `PAGE_ROTATE_REVIEW` forces review. All F01-F08 plans
include `OP_STRUCTURE_TAGS`; B01/B02 have no operations.

## Material identity

Only these text normalizations are non-material: collapse horizontal tab/space
runs to one space; trim tab/space at line boundaries; and join a U+002D
line-end hyphen only where a declared `HYPHENATION_JOIN` covers it. Case,
punctuation variants, line joining, reordering, and numeric changes are
material. A numeric lexeme is a maximal run drawn from digits, spaces,
`. , + - ( ) % / : $ EUR/GBP/YEN symbols` containing a digit; compare its
displayed characters exactly.

## Gates

- G1 immutable source hash and independent object/page inventory.
- G2 page count/order, MediaBox, CropBox, and rotation.
- G3 ordered normalized text/tokens and exact numeric lexemes.
- G4 visible layer versus text layer, including hidden-text poison.
- G5 reading order, heading hierarchy, and layout/tag derivation agreement.
- G6 navigation integrity. It always runs. With no navigation it may PASS only
  when pdfplumber and the stdlib scanner independently return empty inventories.
- G7 table/cell/numeric identity for tables; detection-only for other classes.
  A table outside `TEXT_TABLE`, or nonempty plan for `BENIGN`, is ESC-01 and
  `CLASSIFIER_CONFLICT`.
- G8 independent refusal/active-content scan.
- G9 budgets and harness-provided no-network observation. Missing evidence is
  `NOT_EXERCISED`, never PASS.
- G10 Poppler 150-DPI render/ink comparison, 8x8-pixel minimum regions, maximum
  aggregate unexplained area fraction 0.005.

Statuses are exactly `PASS`, `FAIL`, `NOT_EXERCISED`, `ERROR`.
`NOT_EXERCISED` never means PASS. C2 must derive `/StructTreeRoot`, `/MarkInfo`,
per-page `/StructParents`, marked-content MCIDs, and a ParentTree; otherwise G5
is `NOT_EXERCISED`.

## Disposition precedence

Apply the first matching rule exactly:

1. PR-00 UNRESOLVED -> NOT_VERIFIABLE.
2. PR-01 REFUSE_* -> REFUSE.
3. PR-02 G1 FAIL/ERROR -> NOT_VERIFIABLE.
4. PR-03 CLASSIFIER_CONFLICT -> NOT_VERIFIABLE.
5. PR-04 G8 FAIL -> REFUSE.
6. PR-05 G2 FAIL -> REFUSE.
7. PR-06 G4 FAIL plus anomaly `DIVERGENT` -> REFUSE.
8. PR-07 reconciliation `UNDECLARED_MATERIAL_DELTA`, `OUT_OF_BOUNDS`, or
   `PLAN_ILLEGAL` -> REFUSE.
9. PR-08 any required gate NOT_EXERCISED/ERROR -> NOT_VERIFIABLE.
10. PR-09 G5 FAIL -> REVIEW.
11. PR-10 other G4 FAIL (`DUPLICATE_VERBATIM`) -> REVIEW.
12. PR-11 G3/G6/G7/G10 FAIL -> REFUSE.
13. PR-12 unconfirmed forced-review operation -> REVIEW.
14. PR-13 all required gates PASS, reconciliation `RECONCILED`, no unconfirmed
    forced review -> ACCEPT.
15. PR-14 otherwise -> NOT_VERIFIABLE.

The implementation may accept the frozen disposition specification as a dict,
but must mechanically preserve this order and return the fired rule id.

## Runtime facts

Python 3.12.14; reportlab 4.4.9; pypdf 6.10.0; pdfplumber 0.11.9; Pillow
12.3.0; pdfminer 20251230. Poppler paths are supplied by Main. qpdf, mutool,
Ghostscript, jsonschema, and Ajv are absent. Do not install anything.


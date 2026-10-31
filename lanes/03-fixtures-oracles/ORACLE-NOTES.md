# Lane 03 oracle notes — rationale, expected visible improvement, determinism

Lane: `03-fixtures-oracles`
Date (frozen constant): 2026-09-29
Companion artifacts: `FIXTURE-MANIFEST.json`, `EXPECTED-DISPOSITIONS.json`,
`MUTATION-SPECS.json`, `GENERATOR-SPEC.md`, `SEALED.md`, `validate.py`.

## 1. Purpose and authority

This lane supplies the frozen fixture/oracle pack for the text-native vertical
slice described in `ASSIGNMENT.md` and `inputs/MAIN-GLM-SYNTHESIS.md`
("Smallest experiment that can kill the idea"). Authority order is
`inputs/FINAL-RECONCILIATION.md`, then `ASSIGNMENT.md`, then
`inputs/MAIN-GLM-SYNTHESIS.md`. Where the synthesis asked for a broader
development set (forms, AcroForms, scans), this lane covers only the
text-native slice assigned to it: 8 development fixtures + 4 refusal controls
+ 2 benign controls. Forms and scan fixtures are out of scope for this lane
and are recorded as such rather than approximated.

## 2. No real PDFs were used

Every PDF in this lane is synthetic and was generated inside this project by
`generator/generate_all.py` from hand-authored content about fictional
entities (Harborview Logistics, Cedar & Vane Ltd, Larkspur grants program,
Cedar Hollow Residents Committee, Cedar Hollow Review, Northbridge Supply Co.,
Alder Grange Estate Trust, Hartwell Manufacturing, Riverside Reading Group).
No real, private, medical, financial, or downloaded PDF was read, copied, or
used as a template. All names, figures, and findings are fictional; the
fixtures themselves carry a visible "synthetic fixture" marker so they cannot
be mistaken for real documents downstream.

## 3. Rationale per fixture

- **F01 memo (2 pp, TEXT_SINGLE_COLUMN).** The canonical ugly memo: repeated
  running header/footer on every page (exercises per-page hashing and
  header/footer normalization), literal double spaces, irregular paragraph
  gaps, indents that vary per paragraph, three body families/sizes, and two
  declared line-end hyphenation breaks (`exam-`/`ple`, `oper-`/`ations`).
  No bookmarks: adding an outline is a tidy opportunity. Also the M01
  deletion target.
- **F02 business letter (1 p).** Letter geometry instead of report geometry:
  centered letterhead, right-aligned date, indented address block, one
  double-spaced sentence, irregular gaps. Holds the frozen M02 transposition
  sentence ("invoice"/"receipt").
- **F03 short report (2 pp).** Headings + an inline numeric row set rendered
  as plain text lines (no grid) so numeric lexeme round-trip is exercised
  without table tooling; a footnote-like trailing note at 8.5pt; flat
  bookmarks (4 top-level entries) that exercise hierarchy repair; declared
  `assess-`/`ment` break.
- **F04 agenda/notices (1 p).** The most alignment-ugly page: item indents
  drift 0-18pt, one right-aligned line, centered title, mixed families.
  M06 hidden-text target.
- **F05 two-column article (3 pp).** Order-sensitive: left column fully,
  then right column, per page. Carries the declared `back-`/`log` and
  `condi-`/`tion` breaks and one double space. M03 column-swap target. A
  verifier's reading-order gate (G5) must be able to tell left-first from
  right-first.
- **F06 two-column report (3 pp).** Adds a small numeric table whose four
  frozen lexemes are `1,234.50`, `(500)`, `12%`, `$0.75`, with deliberately
  mixed row bases (the body text says so explicitly). This is the negative
  control for arithmetic "correction": the rows must round-trip verbatim and
  no arithmetic relationship is asserted.
- **F07 dense multi-page report (4 pp).** Repeated header/footer on every
  page, an accurate TOC-like list (2/2/3/4), an internal cross-reference
  phrase ("as detailed in Section 3 (page 3)"), flat bookmarks, declared
  `main-`/`tenance` and `recommend-`/`ations` breaks. M05 bookmark-loss
  target.
- **F08 statement (3 pp, TEXT_TABLE).** A drawn grid with columns Item /
  Quantity / Unit Price / Amount, a repeated header row per page, a TOTAL
  row, thousands separators, a parenthesised negative, and the units note
  "All amounts in USD." M04 numeric-reassignment target
  (`$1,234.50` -> `$1,238.50`).
- **R01-R04 refusal controls.** Each exhibits exactly one refusing feature
  (encryption, signature field, XFA, active content) on an otherwise trivial
  one-page body, so a refusal can only be attributed to that feature. All
  four are built with installed tools only (reportlab body + pypdf low-level
  object surgery; RC4-128 encryption with frozen dummy passwords).
- **B01/B02 benign controls.** Clean typography, uniform spacing, correct
  hierarchical bookmarks; B02 adds one internal GoTo link (page 1 rect ->
  page 2). They prove the verifier is not over-strict: a pipeline that
  "improves" these, or fails any gate on them, is wrong.

Multi-page coverage: F05, F06, F08 (3 pages) and F07 (4 pages) give four
fixtures with >= 3 pages so bookmarks, reading order, and per-page hashing
are meaningful. Every sealed PDF is under 7 KB (limit 200 KB).

## 4. How "visibly cleaner" should manifest per fixture

These are expectations for the builder's plan, not gates; the meaning gates
always govern (section 6).

- **F01:** uniform spacing (no double spaces, regular paragraph rhythm), one
  body family/size, hyphenation joined ("example", "operations" whole),
  header/footer normalized, outline added. Content unchanged.
- **F02:** uniform paragraph gaps, consistent sizes, aligned blocks. Content
  unchanged.
- **F03:** joined hyphenation, consistent indents, outline hierarchy repaired
  to match the four headings, numeric row set aligned without value changes.
- **F04:** consistent indent scheme for agenda items, uniform notices block.
  Content unchanged.
- **F05:** spacing/typography normalized, hyphenation joined, outline added,
  two-column reading order preserved exactly.
- **F06:** same as F05 plus the four lexemes reproduced verbatim with row
  labels attached.
- **F07:** header/footer normalized on all four pages, hyphenation joined,
  flat outline repaired, TOC still accurate, cross-reference intact.
- **F08:** sub-header spacing normalized at most; grid, cells, TOTAL row, and
  units note preserved exactly.
- **B01/B02:** nothing to improve; a candidate that differs visually from the
  source is itself the defect signal.

## 5. Determinism methodology

1. Seeds frozen before generation (`GENERATOR-SPEC.md` section 1): **no RNG
   anywhere**; nominal seed 20260929 is for the record. Mutation modes carry
   nominal seeds 2026092901-2026092906, also unused in computation.
2. `reportlab` canvases use `invariant=1`; metadata (Title/Author/Subject/
   Creator) are constant strings; base-14 fonts only; all text ASCII.
3. `pypdf` post-processing pins the trailer `/ID` to fixed bytes per control
   document; RC4-128 encryption uses frozen dummy passwords and no IV, so
   output is byte-stable.
4. No wall-clock timestamps appear in any PDF or lane artifact; dates in
   content are fictional constants (e.g. "14 January 2027").
5. Proof: `generator/doublegen_check.py` generated the full set (14 sealed
   PDFs + 6 mutants) into `scratch/gen-a` and `scratch/gen-b` and asserted
   pairwise sha256 equality: 20/20 byte-identical, 0 mismatches. Evidence
   table in `SEALED.md`. Only the gen-a copies were promoted to `fixtures/`.
6. Re-verification: `validate.py` re-hashes the sealed PDFs against
   `FIXTURE-MANIFEST.json` at any later time.

Tool gaps found (recorded, not installed): no mutool/qpdf/gs/pikepdf/pdfminer/
PyMuPDF on this machine. Everything needed was achievable with reportlab +
pypdf + poppler (pdftotext/pdfinfo/pdftoppm). Limitation: byte-level
verification of render-mode-3 ink absence here used pdftotext/pypdf text-layer
extraction plus content-stream inspection; pixel-level proof is delegated to
lane 09/10 via pdftoppm (installed).

## 6. The rule that visual preference cannot override a failed meaning gate

A candidate that looks cleaner is acceptable only if every gate listed for
its class in `EXPECTED-DISPOSITIONS.json` passes. One material failure — a
lost token, a changed numeric lexeme, a wrong reading order, a lost bookmark,
hidden text, any geometry change — blocks ACCEPT regardless of how good the
candidate looks or what an aggregate score says. The worst material element
governs. `NOT_EXERCISED` is never `PASS`: a gate with nothing to check carries
no verdict and cannot be counted toward acceptance. Visual preference, A/B
opinions, and scores are recorded for the closure study; they never override
a failed meaning gate.

## 7. Immutability statement

The sealed PDFs under `fixtures/` are immutable. Their sha256 values are
recorded in `FIXTURE-MANIFEST.json` and `SEALED.md` at seal time. If a defect
is ever found in a sealed fixture, the finding is recorded (in a receipt or
the verifier's record), the defect is left in place, and the sealed file is
NOT edited; a corrected fixture would be a new sealed artifact with a new id
or a new seal generation, never an in-place mutation. Mutation candidates
(M01-M06) are not sealed artifacts; lane 09 produces them from the sealed
fixtures or from the generator's frozen mutation modes and treats them as
disposable test inputs.

## 8. Pre-seal spec revisions (honesty record)

Two `MUTATION-SPECS.json` entries were revised **before sealing** (no sealed
file existed yet; seeds and edit semantics unchanged):

- M06 hidden-text position moved (72, 648) -> (72, 770): at y=648 the
  invisible string overlapped visible agenda text and poppler interleaved it
  into visible lines, making the mechanical signature extractor-dependent. At
  the empty top margin every extractor (pdftotext, pypdf) sees the full
  string as its own line.
- M01/M04 `expected_text_signature` tightened: M01's page-2 phrase "the
  exception queue workflow" is intentionally untouched by the page-1 edit;
  M04's Amount cell correctly keeps `$1,234.50` (the document-wide count
  drops 2 -> 1), because the frozen edit changes only the Unit Price cell.

## 9. Numeric-lexeme inventory (descriptive, for G7 implementers)

- F01: `HL-2027-014`, `3`, `4`, `14 January 2027`, `28 January 2027`,
  `3-4`, `Page N of 2`.
- F02: dates `9 February 2027`, `1 March 2027`; address numerals; `PO1 2AF`,
  `PO2 8LL`.
- F03: `118`, `42`, `4,250`, `36%`, `11,300`; footnote `1 July to 30
  September 2026`.
- F04: `11 March 2027`, `19:00`, `14 January 2027`, notice numerals.
- F05: `1,900`, `2024`, `37 percent`, `214`, `90`, `11 percent`.
- F06: `1,234.50`, `(500)`, `12%`, `$0.75` (frozen); `Quarter 1, 2027`.
- F07: `1897`, `1974`, `1998`, `forty-one` (word), `2026/2027/2029`,
  `2,150,000`, `840,000`, `615,000`, TOC page refs `2/2/3/4`.
- F08: `$0.75`, `$2.40`, `$0.08`, `$3.25`, `$0.30`, `$0.12`, `$6.10`,
  `$1.95`, `$1,234.50`, `($250.00)`, amounts `$18.00`...`($500.00)`, TOTAL
  `$878.75`, quantities `24/6/150/12/40/90/4/7/1/2`, `HM-40213`.
- Displayed strings are the identity anchor; parsed numeric values never
  replace them.

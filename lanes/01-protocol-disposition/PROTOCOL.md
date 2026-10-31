# PROTOCOL.md — Frozen Phase 0 protocol for the text-native vertical slice

Lane: `01-protocol-disposition` · Date: 2026-09-29 · Spec version: `1.0.0`

Authority order applied: `inputs/FINAL-RECONCILIATION.md` > `ASSIGNMENT.md` >
`inputs/MAIN-GLM-SYNTHESIS.md` > remaining receipts. This document, and the
machine-readable `DISPOSITION-SPEC.json` alongside it, freeze the acceptance
protocol so that two correct implementations grade the same file identically.
`DISPOSITION-SPEC.json` is normative; this file is its human-readable statement.
`SCENARIOS.json` freezes the six ambiguous cases. `validate.py` proves the
whole pack is mechanically evaluable; its output is `VALIDATION-OUTPUT.txt`.

Slice scope (frozen): **text-native, unsigned, unencrypted, non-active PDFs**;
only the allowed tidy operations below; **page count, page order, and page
boundaries are immutable**. Forms, scans/OCR, and everything else are out of
scope for this slice; their handling here is refusal or out-of-scope routing,
never a pipeline.

---

## 1. Document classes and mechanical classifiers

Classification runs on the immutable source at intake, before any planning or
building. Classifier precedence is mechanical and ordered: the refuse scans run
first (in the order ENCRYPTED, SIGNED, XFA, ACTIVE), then parse-failure, then
table detection, then multi-column detection, then single-column/BENIGN.

| Class | In scope | Mechanical classifier (frozen test) | Handling |
|---|---|---|---|
| `TEXT_SINGLE_COLUMN` | yes | Refusal scan clean AND table detector finds 0 tables AND multi-column detector negative. | Full gate chain; ACCEPT-eligible. |
| `TEXT_MULTI_COLUMN` | yes | Refusal scan clean AND 0 tables AND multi-column detector positive. | Full gate chain; ACCEPT only after G5 two-derivation agreement. |
| `TEXT_TABLE` | yes | Refusal scan clean AND >=1 table detected. | Full gate chain including G7; ACCEPT-eligible with cell/lexeme identity. |
| `REFUSE_ENCRYPTED` | no | `/Encrypt` in trailer or any security handler present. | REFUSE before any build; no candidate; gates not run. |
| `REFUSE_SIGNED` | no | Any signature dictionary: `FT=/Sig` field, `/DocMDP`, `/Perms /Signatures`, or covered `/ByteRange`. | REFUSE before any build. |
| `REFUSE_XFA` | no | `/AcroForm` with `/XFA` (including dynamic/hybrid XFA). | REFUSE before any build. |
| `REFUSE_ACTIVE` | no | `/JavaScript`, `/JS`, `/Launch`, `/EmbeddedFile`, `/GoToR`, `/GoToE` (including `/OpenAction`, name trees, annotations) or pending `/Redact` annotations. | REFUSE before any build. |
| `BENIGN` | yes | Content classifier result is single-column-clean AND the planned operation list is empty (verified `plan.operations == []`). | Control proving the verifier is not over-strict; same gate chain; ACCEPT-eligible with zero deltas. |
| `UNRESOLVED` | no | Any classifier precondition fails (parse failure, decode error, undeterminable layout). | NOT_VERIFIABLE via PR-00; never built. |

Frozen detector constants:

- **Table detector**: a table is a grid of text cells with >= 2 rows and >= 2
  columns that share >= 3 common column x-boundaries and >= 3 common row
  y-boundaries (tolerance 2 pt), adjacent-cell gaps < 36 pt. `table_id` is
  assigned deterministically as `(page_index, detection_order)`.
- **Multi-column detector**: excluding header/footer bands (top and bottom 10%
  of MediaBox height), a page is multi-column iff text spans cluster into >= 2
  column groups separated by a vertical gutter >= 18 pt that no span crosses,
  each cluster spanning >= 50% of the remaining text height. The document is
  TEXT_MULTI_COLUMN iff >= 1 page is multi-column.
- **Escalation (ESC-01)**: G7's detection pass runs on every in-scope class. If
  it detects a table in any class other than TEXT_TABLE (or a non-empty plan in
  a BENIGN document), reconciliation outcome is `CLASSIFIER_CONFLICT` ->
  NOT_VERIFIABLE via PR-03. The classifier and verifier may never silently
  disagree.

Refusal handling is frozen: a REFUSE_* class is refused at intake with a
templated reason family (`refuse/encrypted`, `refuse/signed`, `refuse/xfa`,
`refuse/active`) plus page/region identifiers where available; raw sensitive
document text is never echoed. No candidate is produced; all gates are recorded
`NOT_EXERCISED`; the disposition is REFUSE by PR-01 regardless of gate statuses.
Out-of-scope content discovered after classification (G8 FAIL on an in-scope
class) is refused by PR-04 for the same reason families.

## 2. Material elements and materiality

An element is **material** if changing it can change the document's meaning.
The worst material element governs; no score exists anywhere in this protocol.

1. **Text token** — a maximal run of non-whitespace characters as segmented by
   the verifier extractor at frozen settings. Identity = the normalized string
   (under the whitelist, section 3) at its position in the containing
   reading-order element. Mechanical test: ordered token sequence equality per
   element, and per-page token multiset equality, modulo declared deltas. Any
   difference outside the whitelist and outside declared deltas is material.
2. **Numeric lexeme** — a maximal run of characters from the alphabet
   `[0-9 . , + - ( ) % / : $ € £ ¥]` containing at least one digit. Identity =
   the **exact displayed string, character for character**: leading zeros,
   precision, signs, parentheses, currency symbols, percent, dates, and times
   are all part of identity. **No normalization ever applies to numeric
   lexemes.** Mechanical test: per-page ordered sequence of lexemes from source
   and candidate must be exactly equal. Any difference (string, count, or
   order) is material. No operation may declare a delta over numeric lexemes;
   an observed numeric change is `UNDECLARED_MATERIAL_DELTA`, a declared
   attempt is `PLAN_ILLEGAL` — both REFUSE.
3. **Table cell** — identity = `(table_id, row_anchor, column_anchor)`;
   `row_anchor` = exact normalized text of the row's leftmost cell;
   `column_anchor` = exact normalized text of the column's header cell.
   Mechanical test: identity-set bijection source<->candidate plus per-cell
   content equality (whitelist for non-numeric token text, exact for numeric
   lexemes), preserving row/column order, spans, and header relationships.
   Arithmetic divergence is computed and reported; it is **never corrected**
   and never a gate failure by itself.
4. **Reading-order element** — block unit of type heading (with explicit
   level), paragraph, list item, notice, caption, figure region, table region,
   header instance, or footer instance. Identity =
   `(page, type, level?, normalized anchor-token sequence, ordinal among
   same-type elements on the page)`. Mechanical test: the element sequence must
   be identical source vs candidate modulo declared deltas, and heading
   hierarchy must be valid: the first heading is level 1 and each subsequent
   heading level is <= previous heading level + 1 (no level skips).
5. **Navigation target** — outline/bookmark item, TOC entry, or internal link.
   Identity = `(kind, resolved destination page index, destination coordinates
   within 1.0 pt, title/anchor text under the whitelist)`. Mechanical test:
   bijection source<->candidate (after declared adds/repairs), zero dangling
   destinations, every added/repaired target declared in the plan and
   independently resolved by the verifier.
6. **Visible ink** — rendered marks on the page, measured from an independent
   render (G10). Mechanical test: every material text token in the text layer
   must have visible ink at its span region (G4); ink differences beyond
   declared deltas are material (G10).

**Material visual difference** (frozen): a connected pixel-difference region
between independent renders of source and candidate at 150 DPI whose bounding
box exceeds 8x8 pixels, or an aggregate unexplained diff area exceeding 0.5% of
the page area, that is attributable neither to a whitelisted normalization
effect nor to the declared expected-delta region of a planned operation.

## 3. Normalization whitelist and the expected-delta rule

The whitelist is the **exact finite list** of text normalizations that are NOT
material changes:

- **N-01** — collapse any maximal run of horizontal whitespace characters
  (U+0009, U+0020) to a single U+0020.
- **N-02** — strip runs of U+0009/U+0020 at the start and end of a line.
- **N-03** — join a **declared** line-end hyphenation: `x-` + line break + `y`
  -> `xy`, only for hyphen U+002D, only where declared as a HYPHENATION_JOIN
  operation.

Everything not in this list is **material**, including explicitly: case
folding; dash variants (– — ‐ ‑ vs -); quote variants (' ' " " vs ' ");
currency symbol variants; whitespace-to-nothing (including removing a line
break or joining lines, which also changes line count — line breaks inside a
reading-order element are material structure in this slice because reflow is
out of Phase 0); any reordering; any numeric lexeme change; any glyph
substitution that is not a declared, glyph-verified typography operation.

**Expected-delta rule**: every planned operation declares
`{op_type, anchor (page/element/region ids), expected_delta {type, scope,
bounded magnitude}}`. Delta types are the finite set: SPACING_COLLAPSE,
LINE_END_WHITESPACE_STRIP, ALIGNMENT_SHIFT, GLYPH_SUBSTITUTION,
HYPHENATION_JOIN, HEADER_FOOTER_INSTANCE_NORMALIZATION, STRUCTURE_TAG_ADD,
READING_ORDER_SET, BOOKMARK_ADD, BOOKMARK_DEST_REPAIR, LINK_DEST_REPAIR,
PAGE_ROTATE_REVIEW. Magnitude bounds are per-operation integers/fractions
(max affected tokens, max affected regions, max affected area fraction).
The verifier reconciles observed vs expected: observed material deltas must
each be covered by a declared delta of matching type and scope within bounds.
`GLYPH_SUBSTITUTION` requires glyph verification: the substituted glyph must be
independently extracted back as the intended character and its rendered ink
must match the intended character shape within the declared region; it may
never apply to a numeric lexeme. Allowed operation set (Phase 0): spacing
normalization; alignment normalization; glyph-verified typography; declared
line-end hyphenation joins; repeated header/footer normalization (per detected
instance only — a page lacking the repeated instance is never modified);
structure tags; reading-order set; bookmark add/repair; internal link repair
with independently established destinations; page rotation **only** as the
forced-review operation PAGE_ROTATE_REVIEW.

## 4. Gate registry G1–G10 with independence requirements

Independence is mechanical, not declared: for a gate to count as independent,
the verifying tool (a) must not be the builder's writer library nor share its
decisive code path for that computation, (b) must never be invoked through
builder APIs for that computation, and (c) must be evidenced in lane 04's
`TOOLCHAIN.json` (independent second extractor and independent renderer of
different lineage). A gate run without recorded independence evidence must be
recorded `NOT_EXERCISED`, never PASS.

| Gate | Mechanical checks (summary) | Independence requirement |
|---|---|---|
| **G1** source hash/inventory | SHA-256 of the immutable original re-verified at disposition time equals the intake record; raw object inventory (object count, page-tree nodes, per-page object refs) computed by the verifier parser equals the intake record. | System sha256 utility + verifier's own parser; never the builder's writer or report. |
| **G2** page geometry reconciliation | Page count identical; page order identical: pages outside every declared operation scope have identical normalized-text fingerprints, and the plan's page mapping is the identity; MediaBox/CropBox identical per page; `/Rotate` identical except where a declared PAGE_ROTATE_REVIEW op covers it (recorded, forces REVIEW via PR-12). | Verifier's independent extractor computes geometry. |
| **G3** text identity under whitelist | Per reading-order element, ordered token sequence equality under N-01..N-03 plus declared HYPHENATION_JOIN; per-page numeric lexeme sequences exactly equal; per-page token multisets equal modulo declared deltas. | Second extractor of different lineage from the builder's writer and from the builder's planning-time extractor. |
| **G4** visible-layer vs text-layer agreement | Every material text-layer token has visible ink at its span region; no visible material glyph sequence lacks a text-layer counterpart; hidden-text detection: text-layer tokens with no ink at their location are anomalies, classified DUPLICATE_VERBATIM (identical to the overlapped visible sequence) or DIVERGENT. Any anomaly or mismatch FAILs. | Independent renderer + verifier extractor; not the builder's layout engine. |
| **G5** reading order/hierarchy validity | Element sequence identity (section 2.4) modulo declared READING_ORDER_SET; heading hierarchy validity rule; two independent reading-order derivations (layout-based and structure/tag-based, from different tools) must agree on the candidate wherever both are derivable. | Two independent derivations from different tool lineages. |
| **G6** navigation integrity | Every source navigation target preserved with identical resolved destination (page + coordinates within 1.0 pt) and whitelisted-equal title/anchor; every added/repaired target declared and independently resolved; zero dangling destinations; zero undeclared targets. | Navigation read by the verifier's independent parser. |
| **G7** table cell identity + numeric lexeme identity | For TEXT_TABLE: identity-set bijection of `(table_id, row_anchor, column_anchor)`; cell content equality (whitelist non-numeric, exact numeric); row/column order, spans, header relationships, and external unit declarations preserved; arithmetic divergence reported, never corrected. Elsewhere: detection pass only (ESC-01). | Verifier's own table detector, extractor, and numeric lexer. |
| **G8** active-content/refusal scan | Raw-byte and parsed-object scan of source and candidate for: `/Encrypt`; signature dictionaries; `/XFA`; `/JavaScript`, `/JS`, `/Launch`, `/EmbeddedFile`, `/GoToR`, `/GoToE` (incl. `/OpenAction`, name trees, annotations); pending `/Redact` annotations. PASS = none present. | Verifier's own raw-object scan; never the builder's classification report. |
| **G9** resource budget + no-network | Measured page count, object count, bytes, decoded pixels, CPU time, wall time, temp storage, output size within lane 05's frozen `BUDGETS.json` values; no-network evidence (no socket use during the pipeline) observed by the harness. If `BUDGETS.json` or harness observation is unavailable, G9 is `NOT_EXERCISED`. | Harness/OS-level measurement; never builder self-report. |
| **G10** independent render / ink accounting | Independent renderer renders source and candidate at 150 DPI; per-page ink coverage recorded; pixel-diff regions computed; every region explained by a whitelisted effect or a declared expected-delta region, else material visual difference -> FAIL. Frozen constants: 150 DPI, 8x8 px region threshold, 0.5% aggregate area threshold. | Renderer of different lineage from the builder's writer and from the primary extractor. |

## 5. Gate statuses — exact semantics

- **PASS** — the gate ran to completion with its independence requirement met
  and evidenced, and every mechanical check passed.
- **FAIL** — the gate ran to completion and at least one named mechanical
  check failed (check id recorded).
- **NOT_EXERCISED** — the gate did not run for this document: it is out of
  scope for the class, or a prerequisite was missing (no candidate, missing
  independence evidence, missing budget file). **NOT_EXERCISED never counts as
  PASS.**
- **ERROR** — the gate was attempted but could not produce a verdict (crash,
  verifier-side budget exhaustion, dependency failure). ERROR is treated worse
  than FAIL: a FAIL is a definite adverse finding, an ERROR is a missing proof.

## 6. Class-by-gate matrix and disposition precedence

Matrix values: **REQUIRED** (must run; PASS required for ACCEPT; FAIL /
NOT_EXERCISED / ERROR block ACCEPT per the precedence rules), **NOT_REQUIRED**
(may run and is recorded; does not constrain this class's disposition by
itself), **OUT_OF_SCOPE** (does not apply; expected NOT_EXERCISED; ignored by
the disposition function).

| Class | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 | G10 |
|---|---|---|---|---|---|---|---|---|---|---|
| TEXT_SINGLE_COLUMN | REQ | REQ | REQ | REQ | REQ | REQ | OOS | REQ | REQ | REQ |
| TEXT_MULTI_COLUMN | REQ | REQ | REQ | REQ | REQ | REQ | OOS | REQ | REQ | REQ |
| TEXT_TABLE | REQ | REQ | REQ | REQ | REQ | REQ | REQ | REQ | REQ | REQ |
| BENIGN | REQ | REQ | REQ | REQ | REQ | REQ | OOS | REQ | REQ | REQ |
| REFUSE_ENCRYPTED | NOT_REQ | OOS | OOS | OOS | OOS | OOS | OOS | NOT_REQ | OOS | OOS |
| REFUSE_SIGNED | NOT_REQ | OOS | OOS | OOS | OOS | OOS | OOS | NOT_REQ | OOS | OOS |
| REFUSE_XFA | NOT_REQ | OOS | OOS | OOS | OOS | OOS | OOS | NOT_REQ | OOS | OOS |
| REFUSE_ACTIVE | NOT_REQ | OOS | OOS | OOS | OOS | OOS | OOS | NOT_REQ | OOS | OOS |

Dispositions are `ACCEPT | REVIEW | REFUSE | NOT_VERIFIABLE` per document;
`INVALID_EXPERIMENT` is run-level only (section 9). The disposition is a **pure
function** `dispose(class, gate_statuses, reconciliation)` where the
reconciliation result is `{outcome, anomaly_kind?, plan_forced_review,
undeclared_delta_types?}` (plus `confirmed_uncertainty_ids` on the replay path,
empty and unused in this run). Reconciliation outcomes: `RECONCILED`,
`UNDECLARED_MATERIAL_DELTA`, `OUT_OF_BOUNDS`, `PLAN_ILLEGAL`,
`HIDDEN_TEXT_ANOMALY` (anomaly_kind `DUPLICATE_VERBATIM` | `DIVERGENT`),
`CLASSIFIER_CONFLICT`, `RECONCILIATION_NOT_RUN`. The ordered precedence list,
evaluated first-match-wins (full machine-readable conditions in
`DISPOSITION-SPEC.json`):

- **PR-00** — class `UNRESOLVED` -> **NOT_VERIFIABLE**. (Cannot classify, cannot verify.)
- **PR-01** — class is a `REFUSE_*` class -> **REFUSE**. (Refusal conditions are checked first; gate statuses are irrelevant; no candidate exists.)
- **PR-02** — G1 FAIL or ERROR -> **NOT_VERIFIABLE**. (The original's identity is unproven; no comparison is meaningful.)
- **PR-03** — reconciliation `CLASSIFIER_CONFLICT` -> **NOT_VERIFIABLE**. (The class model is untrusted — ESC-01.)
- **PR-04** — G8 FAIL -> **REFUSE**. (Active/protected content discovered after classification.)
- **PR-05** — G2 FAIL -> **REFUSE**. (Page count, page order, or page boundaries were changed; immutable invariants, never human-resolvable in Phase 0.)
- **PR-06** — G4 FAIL with anomaly_kind `DIVERGENT` -> **REFUSE**. (True hidden-text poison: hidden text diverges from the visible layer — deceptive content.)
- **PR-07** — reconciliation `UNDECLARED_MATERIAL_DELTA` | `OUT_OF_BOUNDS` | `PLAN_ILLEGAL` -> **REFUSE**. (The worst material element governs: any undeclared material text/numeric/table/navigation delta, exceeded bound, or illegal operation refuses the candidate. Declared or not, no allowed operation may touch numeric lexemes.)
- **PR-08** — any REQUIRED gate `NOT_EXERCISED` or `ERROR` -> **NOT_VERIFIABLE**. (A required proof could not be performed; this blocks ACCEPT and is worse than REVIEW.)
- **PR-09** — G5 FAIL -> **REVIEW**. (Named uncertainty U-READING-ORDER: independent reading-order derivations disagree or hierarchy invalid; a human can inspect the page, but the candidate can never auto-ACCEPT.)
- **PR-10** — G4 FAIL otherwise (anomaly_kind `DUPLICATE_VERBATIM`) -> **REVIEW**. (Named uncertainty U-HIDDEN-TEXT: hidden text duplicating visible text verbatim cannot be mechanically declared harmless.)
- **PR-11** — G3, G6, G7, or G10 FAIL -> **REFUSE**. (Definite material text, navigation, table, or visible-ink failure; not resolvable into acceptance.)
- **PR-12** — a forced-review operation (PAGE_ROTATE_REVIEW) is present and unconfirmed -> **REVIEW**. (Policy-forced review, not evidence-forced.)
- **PR-13** — all REQUIRED gates PASS and reconciliation `RECONCILED` and no unconfirmed forced-review operation -> **ACCEPT**.
- **PR-14** — anything else -> **NOT_VERIFIABLE**. (Totality fallback; the protocol never defaults to ACCEPT.)

Structural guarantees: no score exists; ACCEPT is reachable only through
PR-13; every FAIL/NOT_EXERCISED/ERROR of a REQUIRED gate blocks ACCEPT; refusal
and class guards precede content rules; the function is total (PR-14).

## 7. Human-confirmation replay (NOT_EXERCISED this run)

- **CONFIRM resolves exactly one thing**: the named uncertainty attached to the
  fired rule, recorded with decision, identity, and timestamp. In Phase 0 the
  only confirmable uncertainty is **U-FORCED-REVIEW-OP** (raised by PR-12):
  human authorization of the named review-required operation for this document.
  On replay, PR-12 does not fire and the disposition is recomputed by the same
  precedence list; it becomes ACCEPT via PR-13 only if all required gates PASS
  and reconciliation is RECONCILED.
- **CONFIRM may never**: convert any FAIL, NOT_EXERCISED, or ERROR gate status
  into a pass; alter, delete, or recompute any gate record; make an
  out-of-scope or refused class in-scope; or apply to any meaning-preservation
  gate failure. U-READING-ORDER (PR-09) and U-HIDDEN-TEXT (PR-06/PR-10) are
  **not confirmable**: they are meaning-preservation evidence, so those REVIEW
  dispositions remain REVIEW even after a confirmation attempt.
- **This run never exercises human confirmation.** The replay path status is
  `NOT_EXERCISED` for this experiment; no disposition in this run may depend on
  a CONFIRM record.

## 8. "Visibly cleaner" rule

At least one supported fixture with disposition ACCEPT must be observably
improved, judged by verifier-computed, pre-declared criteria (not aesthetics):

- **VC-1** — whitespace anomalies: the count of horizontal-whitespace runs of
  length >= 2 in extracted text decreases, and is 0 on declared pages where
  SPACING_COLLAPSE was applied.
- **VC-2** — alignment: the population variance of left-edge x-coordinates of
  body text span origins decreases within the declared alignment scope by at
  least the declared bound.
- **VC-3** — navigation gain: where BOOKMARK_ADD was declared and the source
  outline was empty or incomplete, the candidate outline resolves >= 1 bookmark
  per top-level heading.

Visual improvement is **never an acceptance gate**: the criteria appear in no
precedence condition, and visual preference can never override a failed
meaning-preservation gate — structurally, because ACCEPT is reachable only via
PR-13 with every required gate PASS.

## 9. Run-level INVALID_EXPERIMENT

Never produced by `dispose()` and never a document disposition. The run is
declared `INVALID_EXPERIMENT` if any frozen trigger fires: sealed inputs or
fixtures modified (hash mismatch); a verifier repairing the candidate it
evaluates; a gate status recorded without required independence evidence; the
holdout opened before protocol freeze; any disposition derived outside this
spec. Document records remain as computed; the run-level flag overrides the
run summary only.

## 10. Honest limits (NOT_READY-style statements frozen here)

- Gate **values** for G9 (budgets) and the concrete tool names for the
  independent second extractor and renderer are **not frozen by this lane**;
  this protocol freezes only the independence requirements and the semantics of
  consuming lane 05's `BUDGETS.json` and lane 04's `TOOLCHAIN.json`. If either
  file is absent, the dependent gates are `NOT_EXERCISED` and the disposition
  is NOT_VERIFIABLE by PR-08 — never PASS by assumption.
- The human-confirmation replay path is defined but `NOT_EXERCISED`.
- Forms, scans/OCR, RTL/bidi, and all other out-of-scope content have refusal
  or NOT_VERIFIABLE handling only; no pipeline is designed or claimed here.
- Detector constants (table, multi-column, render DPI, diff thresholds) are
  frozen values chosen conservatively for the synthetic slice; they are
  mechanical, not proven optimal.

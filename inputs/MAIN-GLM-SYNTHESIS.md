# Main synthesis — online PDF reconstruction after five GLM investigations

Date: 2026-09-29

## Outcome

The product is buildable, but only if the first release is narrower than
"make any PDF prettier." The defensible first product is:

> Take a text-native, unsigned, unencrypted, non-active PDF; produce a visibly
> cleaner and easier-to-navigate PDF using a frozen set of allowed operations;
> then prove text, structure, numeric values, and visible meaning were not
> silently changed.

Tables and existing AcroForms may enter the first experiment only under strict
preservation rules. Scans, inferred forms, consent bindings, hostile files,
encrypted files, signatures, XFA, active content, RTL/bidi, material optional
layers, and ambiguous visible-vs-hidden text do not receive an automatic
ACCEPT in the first release.

This is a standalone product. PDF Workbench is not a Phase 0 dependency. It
may donate isolated, license-compatible implementation ideas later.

## Evidence reviewed

Five exact `glm-5.3-flashx` specialist lanes completed:

1. forms, intake packets, consent, signatures, repeating fields, phone use;
2. dense reports, papers, manuals, legal prose, footnotes and long documents;
3. tables, statements, numeric identity and wide layouts;
4. scans, OCR, mixed raster/vector pages and handwriting;
5. hostile, ambiguous, inaccessible and refusal cases.

Measured run evidence:

- lanes: 5;
- provider responses: 91;
- prompt tokens: 227,436;
- completion tokens: 2,754;
- total tokens: 230,190;
- cached prompt tokens: 223,040;
- all five requested and resolved exactly `glm-5.3-flashx`;
- every lane wrote `GLM-REPORT.md`, `GLM-DECISIONS.json`, and `FINAL.md`;
- all 19 frozen source files rehashed successfully;
- frozen capsule `data/` remained empty.

The first four-way launch exposed a real provider constraint: the fourth
concurrent continuation received HTTP 429. Three concurrent FlashX lanes are
the observed safe ceiling for this account. The failed first attempt is
preserved; the forms lane succeeded when rerun at lower concurrency.

## What all five lanes agreed on

1. A candidate PDF is never the sole record. The original remains immutable.
2. Extraction is observation, not truth. OCR and structure inference remain
   hypotheses until verified.
3. Every visible change must be represented as a named operation with source
   anchors and an expected delta.
4. A percentage score cannot overrule one material failure. The worst
   material element determines the document disposition.
5. `NOT_EXERCISED` is never silently counted as `PASS`.
6. Visible appearance and extracted text must be compared to each other; two
   independent green checks can still describe two different documents.
7. Tables require cell identity, units and numeric lexemes, not token counts.
8. Existing form fields require a complete round trip; inferred fields require
   human confirmation and cannot auto-ACCEPT.
9. Scans must preserve answer ink. A completed scanned form must never be
   "cleaned" into an empty template.
10. Hostile or unsupported inputs must be refused precisely, not coerced into
    the happy path.

## Main decisions that resolve the packet contradictions

### 1. Define the Phase 0 tidy set

Phase 0 may apply only these operations:

- normalize spacing within a preserved page boundary;
- normalize alignment without changing reading order or cell attachment;
- normalize typography using glyph-verified substitutions;
- join declared line-end hyphenation only;
- normalize repeated headers and footers without deleting unique content;
- add or repair structure tags;
- set verified reading order;
- add or repair bookmarks and outline entries;
- repair internal navigation only when the destination is independently
  established;
- rotate a page only as a named REVIEW operation.

Page order is immutable. Page count and page boundaries are invariant for the
first release. Reflow, summarization, paraphrase, row/column changes, field
semantic changes and page regrouping are outside Phase 0.

### 2. Narrow automatic ACCEPT

Automatic ACCEPT is initially available only for:

- text-native documents with verified text identity and reading order;
- ordinary single-column documents;
- simple multi-column documents after independent reading-order agreement;
- tables whose cell grid, headers, units and numeric lexemes all round-trip;
- existing AcroForms with a complete field-tree/value/widget round trip and no
  JavaScript, XFA, signature or ambiguous appearance state.

Everything else is REVIEW, REFUSE or NOT_VERIFIABLE.

### 3. Conservative forms policy

- Preserve existing AcroForm field names, types, flags, values, options,
  on-values, widget rectangles and defined tab order exactly.
- Do not normalize dates, phone numbers, ZIP codes, checkbox values or case.
- Do not infer required flags, calculations or validation rules.
- Do not create `/Sig` fields.
- Independent Yes/No checkboxes are never auto-converted to radio groups.
- Consent paragraph-to-checkbox bindings require a human confirmation pass.
- Phase 0 emits an inferred field map only; it does not place inferred widgets
  into the candidate until a human confirms them.
- JavaScript-bearing forms are REFUSE in Phase 0. A later experiment may test
  strip-with-finding, but Phase 0 does not silently remove behavior.
- Mobile measurements are reported, not a Phase 0 acceptance gate.

### 4. Conservative tables policy

- Stable identity is `(table_id, row_anchor, column_anchor)`, not page order.
- Preserve displayed strings exactly: leading zeroes, decimal precision,
  signs, parentheses, dashes, blanks, currencies, percentages and dates.
- Preserve row/column order, spans, header relationships and external unit
  declarations such as "in thousands."
- Numeric parsing is verification-only. Parsed numbers never replace rendered
  source strings.
- Arithmetic checks detect divergence; they never "correct" the document.
- Wide-table splitting, transposition or reflow is REVIEW-only and outside the
  automatic Phase 0 path.
- CSV/HTML/JSON companions may be evidence, never the authoritative product.

### 5. Conservative scan/OCR policy

- OCR is a searchable companion layer, never source truth.
- The original raster remains the visible meaning-of-record for scans.
- Recognition confidence propagates from character to token to element to
  document disposition; the weakest material token wins.
- Answer ink, stamps, marginalia, checkmarks, strikethroughs and handwriting
  are content.
- Same-engine extraction and verification do not count as independence.
- A scan cannot be marketed as "prettier" merely because OCR was added. Its
  measurable benefit is searchability and usability.
- Scanned numeric tables and completed scanned forms cannot auto-ACCEPT in the
  first release.

### 6. Conservative hostile-input policy

Phase 0 refuses:

- encrypted PDFs regardless of apparent decryptability;
- signed or certified PDFs;
- XFA or hybrid XFA;
- active actions, JavaScript, launch actions, embedded files and external
  executable targets;
- pending redactions;
- conservative-parser failures;
- decode-budget, object-count, nesting or wall-clock limit exceedances;
- material RTL/bidi, optional-content-layer dependence or unsupported complex
  scripts;
- material text without a verified glyph mapping;
- identity/value pseudo-redactions where live text exists under opaque ink;
- any file whose required security verification did not run.

Refusal messages use templated reason families plus page/region identifiers.
They do not echo raw sensitive document text.

## Document dispositions

Every input receives exactly one mechanically computed disposition:

- `ACCEPT`: all required checks passed and no unresolved material hypothesis;
- `REVIEW`: a named content uncertainty can be resolved by a human;
- `REFUSE`: the pipeline cannot safely process the file under the frozen
  policy;
- `NOT_VERIFIABLE`: a required content proof could not be performed;
- `INVALID_EXPERIMENT`: the run violated its own frozen protocol.

Report-writing code cannot choose ACCEPT. ACCEPT is derived from verification
records and the content model.

## Required representation

Build one Common Document Reconstruction Record (CDRR) containing:

- source object inventory and immutable source hashes;
- pages in canonical point coordinates;
- text spans and glyph mappings;
- headings with explicit levels;
- paragraphs, lists, notices, captions and figures;
- reading order and confidence;
- tables, cells, spans, headers, units and numeric lexemes;
- footnote/endnote/citation/reference relationships;
- bookmarks, outline, TOC and internal link destinations;
- form tree, widgets, values, appearance states and proposed side-map names;
- visible-ink regions, scan/OCR alternatives and confidence;
- every planned operation, source anchor, justification and expected delta;
- every verifier result and independence declaration;
- final disposition derived from those records.

## Verification chain

The first implementation must separate builder and verifier paths where
possible and run these gates:

1. immutable source hash and raw object inventory;
2. source/candidate page geometry and object reconciliation;
3. raw and normalized text identity under a frozen normalization whitelist;
4. visible-layer versus text-layer agreement for material content;
5. reading-order and hierarchy validity;
6. footnote/endnote/citation/TOC/bookmark/link integrity;
7. table cell identity, units, numeric lexemes and arithmetic divergence;
8. AcroForm field/value/widget round trip;
9. independent-renderer visual and ink accounting;
10. active-content, attachment, encryption, signature and redaction scan;
11. resource-budget and no-network observations;
12. human A/B usability study under a frozen paired protocol.

No verification stage may silently repair the candidate it is judging.

## Smallest experiment that can kill the idea

Do not start with the full 100-document promise. First prove a vertical slice:

### Development set

- 4 text-native single-column PDFs;
- 4 multi-column/dense-report PDFs;
- 4 data-heavy/table PDFs;
- 4 AcroForms, including filled and empty examples;
- 4 refusal controls covering encryption, signature, XFA and active content;
- synthetic mutations for deletion, transposition, wrong reading order,
  numeric reassignment, checkbox change, bookmark loss and hidden-text poison.

### Holdout

- 10 unopened documents balanced across the supported classes and controls.

### Kill conditions

Stop or redesign if any of these occur:

- one seeded material mutation survives undetected;
- one ACCEPT candidate loses or changes a material token/value/cell/field;
- the independent visual/text comparison cannot distinguish hidden-text poison;
- reviewers do not prefer the candidate on the predeclared supported class;
- human review takes as long as manual reconstruction;
- refusal precision is too low to make batch use practical.

Only after this vertical slice passes should the experiment expand toward the
larger 100-document cohort.

## Batch and online architecture

For later online/batch use:

- fetch into an immutable content-addressed source store;
- verify MIME by bytes, not extension;
- one expendable worker per document with CPU, memory, decode, object, page,
  pixel and wall-clock budgets;
- network disabled during parsing/reconstruction/verification;
- sensitivity/publication class is part of every cache key;
- no real document is used as training data;
- no cross-document memory or temporary-file reuse;
- atomic per-document outputs and resumable batch manifests;
- failures are isolated per document; one hostile file cannot kill the batch;
- report bundles are static, escaped and free of executable document content;
- page-indexed review for long documents;
- originals and all failed attempts remain preserved.

## Recommended build sequence

1. **Foundation:** CDRR schema, immutable intake, classification, refusal
   engine, manifests, resource budgets and synthetic fixture generator.
2. **Text-native vertical slice:** constrained tidy operations, PDF writer,
   text/layout/reading-order verification, review packet.
3. **Tables:** cell identity and numeric verification without reflow.
4. **Existing AcroForms:** exact round trip; no inference or scripts.
5. **Scans/OCR:** image-preserving searchable companions and review flow.
6. **Inferred forms and consent:** only after explicit human-confirmation UX.
7. **Online batch service:** only after local correctness and security gates
   pass.

## Current readiness verdict

`READY_FOR_COMPOSER_IMPLEMENTATION_READINESS_REVIEW`

This does not authorize a production build, install, upload service or public
deployment. The next step is the already-authorized three-wave Composer review:
five MiMo seats, five DeepSeek seats, then five SWE seats, using this synthesis
as the common evidence packet.


# INVARIANTS — frozen record-keeping and protocol invariants

Lane: `02-cdrr-receipts` (wave A) · Date: 2026-09-29 · Status: FROZEN for the
text-native vertical slice.

Authority order: `inputs/FINAL-RECONCILIATION.md`, then `ASSIGNMENT.md`, then
`inputs/MAIN-GLM-SYNTHESIS.md`, then remaining receipts. These invariants bind
every producer and consumer of a CDRR (`CDRR-SCHEMA.json`) and of any receipt
(`RECEIPT-SCHEMA.json`). They are written to be mechanically checkable; the
check method column names the artifact that performs the check. `validate.py`
in this lane verifies that every id below is cross-referenced inside both
schemas.

## Standing semantics

- Gate statuses are exactly `PASS | FAIL | NOT_EXERCISED | ERROR`.
  `NOT_EXERCISED` is a first-class state and is never counted as `PASS`
  (INV-08). `ERROR` means the check ran and failed operationally.
- Document dispositions are exactly `ACCEPT | REVIEW | REFUSE | NOT_VERIFIABLE`.
  `INVALID_EXPERIMENT` is a run-level outcome, not a document disposition; when
  fired it overrides every document disposition of that run (INV-23).
- Uncertainty is carried in envelope `status` fields (`EXERCISED |
  NOT_EXERCISED | ERROR`); closed-vocabulary enums stay pure.
- Every machine-firable `INVALID_EXPERIMENT` condition has an id `E01`–`E15`
  (catalog in `RECEIPT-SCHEMA.json`, `x-invalidation-condition-catalog`).

## Invariant table

| ID | Invariant statement | Mechanical check method | Violation means |
|---|---|---|---|
| INV-01 | Original file byte-immutability: the sealed source PDF's sha256 and byte size recorded at intake are identical before the run, after every stage, and after the whole experiment; the original is never written to. | Recompute sha256 of the source before and after every run; compare to `document_identity.sha256` / `input_identity.sha256` and to the sealed fixture manifest. | `INVALID_EXPERIMENT` (E01_SOURCE_BYTES_MODIFIED); run receipt records the breach. |
| INV-02 | Page count invariance: candidate page count equals source page count. | Gate G02 compares `pages.records` length against candidate page count from the independent extractor. | Gate FAIL -> disposition cannot be ACCEPT; a change that escapes its gate is `INVALID_EXPERIMENT` (E10). |
| INV-03 | Page boundary invariance: per-page MediaBox and CropBox (canonical points) are unchanged between source and candidate. | Gate G02 compares per-page boxes in the CDRR against independently extracted candidate boxes. | Gate FAIL -> no ACCEPT; undetected change is `INVALID_EXPERIMENT` (E10). |
| INV-04 | Page order invariance: source page i content corresponds to candidate page i for all i. | Gate G02/G03 compare the ordered sequence of per-page content digests. | Gate FAIL -> no ACCEPT; undetected change is `INVALID_EXPERIMENT` (E10). |
| INV-05 | Reading order changes only via a named frozen operation: any reading-order difference between source and candidate maps to exactly one planned and applied `SET_VERIFIED_READING_ORDER` operation. | Diff source-vs-candidate reading order; join against `operation_plan.records` + `applied_operations.records` + `delta_reconciliation.records`. | Reconciliation DIVERGED -> disposition downgrade (no ACCEPT); an unnamed/fabricated operation is `INVALID_EXPERIMENT` (E15). |
| INV-06 | Verifier never repairs: there is no code path from any verifier component to a candidate artifact; the verifier holds read-only access to everything it judges. | Process write-scope audit + candidate hash/mtime check before and after verification; code-path review at Gate A. | `INVALID_EXPERIMENT` (E03_VERIFIER_REPAIRED_CANDIDATE). |
| INV-07 | Builder/verifier separation points are named: the second extractor, the independent renderer, and the disposition engine are distinct named tools from the builder path, with per-gate independence declarations. | `RunReceipt.toolchain` component roles + `VerifierRecord.independence_class`; a decisive gate not declared `INDEPENDENT_IMPLEMENTATION` may not contribute to ACCEPT. | Decisive gate downgraded (no ACCEPT from it); ACCEPT recorded anyway -> `INVALID_EXPERIMENT`. |
| INV-08 | NOT_EXERCISED is never counted as PASS: no consumer (disposition engine, reports, closure) maps `NOT_EXERCISED` to a passing state; required-but-not-exercised gates block ACCEPT. | Disposition-engine unit check; machine diff of `disposition.derivation.gate_statuses` against verifier records. | `INVALID_EXPERIMENT` (E04_NOT_EXERCISED_COUNTED_AS_PASS). |
| INV-09 | Receipts for every run: every per-document run - ACCEPT, REVIEW, REFUSE, NOT_VERIFIABLE, budget-tripped, or crashed - produces a RunReceipt, and the experiment produces an ExperimentRunReceipt. | Count runs vs receipts; assert one RunReceipt per run id; crashed runs carry `crash_evidence.receipt_preserved=true`. | Missing receipt -> `INVALID_EXPERIMENT` (E11_RECEIPT_MISSING_FOR_A_RUN). |
| INV-10 | Atomic outputs: every persistent output is written to a temporary path in the same target directory and then atomically renamed; no partial final artifact ever exists. | Write-path audit; trip-case test; `candidate.written_atomically` must be true whenever a candidate was written. | `INVALID_EXPERIMENT` (E12_NON_ATOMIC_OUTPUT_WRITE). |
| INV-11 | Private temp lifecycle: temporary state is per-document, created under a frozen prefix, removed at dispose (or preserved as crash evidence), and never reused across documents or runs. | `temp_directory_lifecycle` fields (`reused_across_documents` must be false) + trip cases + filesystem audit. | `INVALID_EXPERIMENT` (E07_TEMP_STATE_REUSED_ACROSS_DOCUMENTS). |
| INV-12 | No network during processing: parsing, reconstruction, and verification run with network disabled and audited. | `no_network_evidence` per run; observer/socket audit; a run without `VERIFIED_NO_NETWORK` evidence may not yield ACCEPT. | `INVALID_EXPERIMENT` (E06_NETWORK_USED_DURING_PROCESSING). |
| INV-13 | Output redaction: refusal messages and human-readable summaries use templated reason families plus page/region identifiers only; raw document text is never echoed into refusals, notes, or summaries. (The CDRR itself is the evidence record and legitimately stores extracted text.) | Template-family diff of every refusal/summary string against the frozen reason vocabularies. | `INVALID_EXPERIMENT` (E13_DOCUMENT_TEXT_ECHOED_IN_REFUSAL). |
| INV-14 | Provenance preservation: every integrated artifact is traceable to its producing lane and tool via recorded ids, hashes, and provenance references. | Manifest walk: each integrated file resolves to a lane-written artifact with matching hash. | `INVALID_EXPERIMENT` (E14_PROVENANCE_LOST). |
| INV-15 | Frozen operation-set closure: every planned and applied operation name is one of the ten frozen allowed operations; no other operation exists in this experiment. | Enum check of `operation_name` in CDRR and OperationRecords (schema-enforced). | `INVALID_EXPERIMENT` (E15_SELF_REPAIR_OR_UNFROZEN_RETRY). |
| INV-16 | Hash format integrity: every hash field is 64-character lowercase hex sha256 and is recomputable from the artifact it anchors. | Schema pattern check (validate.py) + recomputation spot checks. | Schema-invalid record; receipt rejected; repair before any disposition is published. |
| INV-17 | Glyph-mapping prerequisite: `NORMALIZE_TYPOGRAPHY` only over spans whose `glyph_mapping_status` is `VERIFIED`; material text with unverified glyph mapping is a refusal family, not a tidy target. | Join typography operations against span glyph statuses. | Operation refused; DIVERGED -> disposition downgrade; tolerated knowingly -> `INVALID_EXPERIMENT` (E15). |
| INV-18 | Refusal precision: every refusal records its `refusal_family` plus evidence anchors, and benign controls must not be refused (guards against over-refusal as well as over-acceptance). | Refusal-control and benign-control tables in the ExperimentRunReceipt; `matched` flags must be true. | Control mismatch -> experiment cannot claim `VERTICAL_SLICE_VERIFIED` (closure failure, recorded honestly). |
| INV-19 | Determinism: a rerun from clean temp state reproduces candidate hashes and record digests, modulo fields declared in `intentionally_variable_fields_declared`. | Rerun comparison; unexplained mismatches are recorded as `MISMATCH`. | Unexplained mismatch -> closure cannot claim `VERTICAL_SLICE_VERIFIED`; declared mismatches only. |
| INV-20 | ACCEPT derivation only: ACCEPT (and every disposition) is the output of the frozen disposition derivation over verification records plus the fired precedence rule; report/summary code has no authority to set a disposition. | Diff reported dispositions against `disposition.derivation` inputs; engine is the only writer of dispositions. | `INVALID_EXPERIMENT` (E05_REPORT_CODE_CHOSE_ACCEPT). |
| INV-21 | Expected-delta reconciliation: every applied operation has a reconciliation result; material divergence blocks ACCEPT. | Join `applied_operations` vs `delta_reconciliation` vs OperationRecords. | Missing reconciliation -> disposition downgrade to REVIEW/NOT_VERIFIABLE; ignored divergence -> `INVALID_EXPERIMENT` (E15). |
| INV-22 | Refuse-shape completeness: a CDRR for a REFUSED document keeps every extraction section present with status `NOT_EXERCISED` (or `ERROR` on mid-write crash) and empty records arrays - empty and explicit, never missing keys. | Schema if/then clause in `CDRR-SCHEMA.json` (validated by validate.py against the refused fixture and its negative). | Schema-invalid record; run receipt cannot be published until fixed. |
| INV-23 | Run-level precedence: `INVALID_EXPERIMENT` is recorded only in the ExperimentRunReceipt and overrides every document disposition of that run; document receipts are preserved unchanged for audit. | ExperimentRunReceipt `run_outcome` + non-empty `invalidation_conditions`; document receipts left untouched. | Any other placement of INVALID_EXPERIMENT -> schema-invalid; conditions list empty with outcome set -> schema-invalid. |
| INV-24 | Record immutability: receipts, verifier records, and CDRRs are append-only; corrections are new superseding records referencing the old one; `schema_version` never changes silently. | Hash chain check across receipt versions; supersede references. | `INVALID_EXPERIMENT` (protocol falsified by rewritten evidence). |

## INVALID_EXPERIMENT condition cross-reference

| Condition id | Triggering condition (frozen) | Primary invariants |
|---|---|---|
| E01_SOURCE_BYTES_MODIFIED | Sealed source bytes changed during or after a run | INV-01 |
| E02_HOLDOUT_OPENED_BEFORE_PROTOCOL_FREEZE | Holdout opened before protocol freeze | (fixture-pack rule; audited at Gate A / closure) |
| E03_VERIFIER_REPAIRED_CANDIDATE | Verifier wrote to or repaired the candidate | INV-06 |
| E04_NOT_EXERCISED_COUNTED_AS_PASS | NOT_EXERCISED treated as PASS by any consumer | INV-08 |
| E05_REPORT_CODE_CHOSE_ACCEPT | Report/summary code set a disposition | INV-20 |
| E06_NETWORK_USED_DURING_PROCESSING | Network used during processing | INV-12 |
| E07_TEMP_STATE_REUSED_ACROSS_DOCUMENTS | Temp state reused across documents/runs | INV-11 |
| E08_ORIGINAL_NOT_PRESERVED | Original or failed attempts not preserved | INV-01, INV-09 |
| E09_UNSEALED_OR_UNHASHED_INPUT_SUBSTITUTED | Input substituted without sealed provenance | INV-15, INV-16 |
| E10_PAGE_COUNT_OR_ORDER_CHANGED_SILENTLY | Page count/order/box change escaped its gate | INV-02, INV-03, INV-04 |
| E11_RECEIPT_MISSING_FOR_A_RUN | A run (refusal or crash included) has no receipt | INV-09 |
| E12_NON_ATOMIC_OUTPUT_WRITE | Output bypassed temp-then-rename | INV-10 |
| E13_DOCUMENT_TEXT_ECHOED_IN_REFUSAL | Document text echoed into refusals/summaries | INV-13 |
| E14_PROVENANCE_LOST | Integrated artifact not traceable to its lane | INV-14 |
| E15_SELF_REPAIR_OR_UNFROZEN_RETRY | Self-repair, unfrozen retry, or non-frozen operation | INV-05, INV-15, INV-17, INV-21 |

## Dependency and conflict notes (honest, frozen at wave A)

1. The class-by-gate required matrix, disposition precedence rule ids
   (`PR-*`), and REVIEW/CONFIRM replay semantics are owned by lane
   `01-protocol-disposition` (`DISPOSITION-SPEC.json`). This lane freezes the
   record shapes and the requirement that the fired rule id be recorded; it
   does not invent precedence content. Sample records use placeholder rule ids
   (`PR-PLACEHOLDER-01`, `PR-REFUSE-PHASE0`) until lane 01 freezes the real
   vocabulary; if lane 01's ids do not match the `^PR-[A-Z0-9-]{1,40}$`
   pattern, the pattern is widened by a recorded schema-version bump, never by
   silent edits.
2. Budget ids, limits, and trip semantics are owned by lane
   `05-safety-budgets` (`BUDGETS.json`); receipts reference them by id.
3. Fixture ids, mutation specs, and seeds are owned by lane
   `03-fixtures-oracles`; receipts reference them by id.
4. Tool names, versions, and independence classes are owned by lane
   `04-dependencies-independence` (`TOOLCHAIN.json`); receipts record what was
   actually used.
5. Where this file and a later frozen lane conflict, the conflict is surfaced
   to the integrator and Gate A; rules are never weakened silently (per
   ASSIGNMENT.md hard boundaries). Any deviation is recorded honestly rather
   than resolved by invention.

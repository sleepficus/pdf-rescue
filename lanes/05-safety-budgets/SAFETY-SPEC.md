# SAFETY-SPEC — frozen safety, budget, and fail-closed behavior for the text-native vertical slice

Lane: `05-safety-budgets` · Date (frozen constant): 2026-09-29 · Status: `FROZEN`
Authority order applied: `inputs/FINAL-RECONCILIATION.md` > `ASSIGNMENT.md` > `inputs/MAIN-GLM-SYNTHESIS.md` > remaining sealed receipts and lane packs.
Consumers: lane 01 gate **G9** (resource budget + no-network) == lane 02 gate **`G11_RESOURCE_BUDGET_NO_NETWORK`**; lane 02 `RunReceipt.budgets[]` (budget ids and statuses); lanes 06/09/10 audits. This lane freezes values, units, measurement points, and trip semantics; it does not assign tool roles (lane 04 `TOOLCHAIN.json` owns that) and does not invent measurements.

## 1. Scope and isolation model

- **Budget unit**: one document run — `intake -> preflight -> extract -> plan -> apply -> verify -> dispose` — for exactly one document, with private per-run temporary storage and no cross-document state (INV-11).
- **Inputs covered**: the 14 sealed fixtures (F01–F08, R01–R04, B01–B02), lane 03 mutants M01–M06, and harness-synthetic trip probes. Nothing else. Sealed fixture bytes are never modified (INV-01/E01).
- **Honesty boundary**: this is a synthetic local vertical slice on one observed machine. No production-service, arbitrary-PDF, or universal performance claim is made or implied.

## 2. Claim labels used in this packet

- **FACT** — read directly from the sealed packet (primarily `ENVIRONMENT-INVENTORY.md`, lane 01/02/03 frozen files).
- **INFERENCE** — derived arithmetically or by mechanical argument from FACTs; derivation always stated.
- **FROZEN DECISION** — a value or rule this lane freezes; justified, not measured.
- **UNKNOWN** — not knowable from the packet; preserved as unknown with the moment it becomes known stated. UNKNOWN never counts as PASS (INV-08, lane 01 §5).

**FACT (baseline)** — `ENVIRONMENT-INVENTORY.md`, observed 2026-09-29, one bounded observation, explicitly "not universal performance claims": max pages 4 (F07); max source bytes 6,969 (F07); max `pdftotext -layout` wall 0.04 s (F01); max `pdftoppm -png -r 150` wall 4.96 s (F01); max render bytes at 150 DPI 461,550 (F07); refusal controls 1,856–2,314 bytes, 1 page each.
**INFERENCE (page geometry)** — US Letter at 150 DPI renders 1275 × 1650 = 2,103,750 px/page; sealed worst-case render need (source + candidate, 4 pages) = 16,830,000 px.
**FACT (version tension, unresolved here, surfaced not patched)** — `ENVIRONMENT-INVENTORY.md` observes Python 3.12.14 / reportlab 4.4.9 / pypdf 6.10.0, while `FIXTURE-MANIFEST.json` records sealing with Python 3.12.7 / reportlab 5.0.1 / pypdf 6.14.2. Budgets are sized to file/page/pixel magnitudes, not tool speed, so the tension does not affect budget values; Gate A / lane 06 must record actual run-time versions (INV-07/INV-14) and adjudicate.

## 3. Frozen budgets

All eight budget ids are exactly the `RunReceipt.budgets[].budget_id` enum of `RECEIPT-SCHEMA.json`. Every budget uses comparison `measured <= limit`. Values, units, baselines, headroom, and rationale are frozen in `BUDGETS.json` below and are restated here in summary:

| Budget id | Frozen limit | Unit | Baseline status | Headroom |
|---|---:|---|---|---:|
| PAGE_COUNT | 8 | pages | MEASURED max 4 | 2× |
| OBJECT_COUNT | 1,000 | indirect objects | UNKNOWN (not in packet) | ~2.9× a mechanical byte-ceiling (~348) |
| FILE_BYTES | 204,800 | bytes | MEASURED max 6,969 | 29.4× |
| PIXELS | 64,000,000 | decoded pixels | DERIVED max 16,830,000 | 3.8× (backstop) |
| CPU_SECONDS | 600.0 | cpu-s (user+system) | UNKNOWN (wall only in packet) | ≥ ~60× inferred |
| WALL_SECONDS | 600.0 | wall-s | DERIVED from components ≈ 10.0 s | ~60× |
| TEMP_STORAGE_BYTES | 104,857,600 | bytes | DERIVED need ≈ 2 MB | ≥ 50× |
| OUTPUT_BYTES | 1,048,576 | bytes | UNKNOWN (no candidate exists) | ~100× tripwire over expectation |

Freeze notes (FROZEN DECISION unless labeled):

- **FILE_BYTES = 204,800** deliberately equals lane 03's frozen ceiling "every sealed PDF < 200 KB" (`GENERATOR-SPEC.md` §5), so input size policing cannot disagree with the fixture pack.
- **PAGE_COUNT = 8** caps the slice at 2× the sealed max; any larger input refuses at intake as out-of-slice. Candidate page count additionally must equal source (INV-02); that equality is gate G2's check, the budget is the ceiling.
- **OBJECT_COUNT = 1,000** — UNKNOWN baseline preserved: no object counts exist in the packet. INFERENCE: a classic xref spends ≥ ~20 bytes per object, so the 6,969-byte max fixture mechanically cannot exceed ~348 objects; 1,000 is ≈ 2.9× that ceiling. The first pipeline run must record actual per-fixture counts.
- **PIXELS = 64,000,000** is a defensive backstop: unreachable while PAGE_COUNT ≤ 8 and `render_dpi = 150` hold; it catches renderer-parameter drift or repeated render loops.
- **CPU_SECONDS / WALL_SECONDS = 600.0** guarantee termination of a runaway worker with generous headroom (~60× the worst observed component sum ≈ 10 s: 0.04 s extract + 2 × 4.96 s renders). CPU baseline is UNKNOWN (inventory supplies wall only); first run records actuals.
- **TEMP_STORAGE_BYTES = 100 MiB** vs a derived worst need ≈ 2 MB (source render set ≤ 461,550 B + candidate render set ≤ 2× + candidate ~source scale + extraction text + CDRR).
- **OUTPUT_BYTES = 1 MiB** is a tripwire, not a target; expected candidate magnitude is source scale (< ~10 KiB including added outline/structure tags). UNKNOWN until a builder exists.
- **Frozen constants consumed by other gates** (do not restated elsewhere): `render_dpi = 150`, page box 612 × 792 pt, render pixel size 1275 × 1650, `pixels_per_page_at_render_dpi = 2,103,750`. Lane 01 G10 / lane 02 G09_INDEPENDENT_RENDER_INK consume `render_dpi`; this lane owns the pixel accounting arithmetic only.

## 4. Measurement points and harness methods

All measurement is harness/OS-level or stdlib-based; builder self-report is never decisive (lane 01 G9 independence). If a measurement point cannot be realized, that budget is recorded `NOT_EXERCISED` (`observed = null`) and lane 01 G9 cannot be PASS → NOT_VERIFIABLE via PR-08 for in-scope classes. Fail closed.

| Budget id | Measured at | Method (stdlib, no installs) |
|---|---|---|
| PAGE_COUNT | source at intake (parser); candidate at verify (independent extractor named in lane 04 `TOOLCHAIN.json`) | parser page count; `pdfinfo`/extractor page count |
| OBJECT_COUNT | intake conservative-parser inventory; verifier re-inventory (feeds G1/G2) | parser object walk |
| FILE_BYTES | intake byte check, before parse; must equal sealed manifest size + sha256 (INV-01) | `os.path.getsize` + sha256 |
| PIXELS | render accounting, per rendered page set (source + candidate) | pages × 1275 × 1650 at 150 DPI; cross-check PNG dimensions with installed Pillow; both recorded |
| CPU_SECONDS | harness-owned, whole run | `resource.getrusage(RUSAGE_SELF)` utime+stime delta, plus `RUSAGE_CHILDREN` delta covering waited-for poppler children |
| WALL_SECONDS | harness-owned, whole run | `time.monotonic()` delta |
| TEMP_STORAGE_BYTES | sampled at every stage boundary and at any trip; maximum recorded | sum of file sizes under the private temp dir |
| OUTPUT_BYTES | candidate write time, before rename | `os.path.getsize` of the temp candidate |

Sampling cadence is frozen so the checks are mechanical and reproducible. Nothing here requires network, installs, or services.

## 5. Trip semantics (fail closed)

**Common trip protocol — every trip, without exception:**
1. Stop at the measurement point; no later stage starts.
2. Discard the partial candidate: delete temp candidate files; never rename or publish; `candidate.written = false`.
3. Re-verify the original: sha256 and byte size must equal intake and sealed-manifest records (INV-01); record the re-verification.
4. Write the `RunReceipt` atomically (INV-09/INV-10): tripped budget `EXCEEDED`; disposition **REFUSE** with `refusal_family = RESOURCE_BUDGET_EXCEEDED` (frozen value in `RECEIPT-SCHEMA.json`); stages after the trip point `NOT_EXERCISED` with reason code `BUDGET_TRIP_BEFORE_GATE`.
5. Remove the private temp dir with removal evidence (timestamp + post-removal listing digest), or retain as crash evidence (`RETAINED_FOR_CRASH_EVIDENCE`) with a content manifest.
6. No repair, retry, or regeneration outside the frozen plan (E15). Net fail-closed state: **original unchanged + receipt present + zero published candidate bytes.**

**Disposition mapping (mechanical, recorded honestly, never patched):**
- Builder-side trip before any candidate → run REFUSE, family `RESOURCE_BUDGET_EXCEEDED` (per `FINAL-RECONCILIATION.md` correction item 14).
- Verifier-side budget exhaustion → the gate records **ERROR** (worse than FAIL, lane 01 §5) → disposition **NOT_VERIFIABLE via PR-08**; the candidate is never published as ACCEPT.
- Post-hoc budget FAIL on a completed candidate → lane 01 **G9 FAIL** / lane 02 **G11 FAIL** recorded. FACT: no precedence rule maps a G9 FAIL to REFUSE or REVIEW; the frozen disposition therefore falls to **PR-14 NOT_VERIFIABLE**. This mapping is recorded as-is for lane 06 review; lane 05 does not invent a harsher rule.
- Network use observed → **run-level `INVALID_EXPERIMENT`** with condition `E06_NETWORK_USED_DURING_PROCESSING`; overrides document dispositions (INV-23); receipt preserved.
- Status semantics: `WITHIN_BUDGET` = measured and `<= limit`; `EXCEEDED` = measured and violated (trip or post-hoc FAIL per above); `NOT_EXERCISED` = never counts as PASS (INV-08); `ERROR` = the measurement itself failed, treated worse than FAIL (lane 01 §5).

## 6. Atomic output behavior (INV-10)

Every persistent output (candidate PDF, CDRR, receipts, render PNGs) is written to a temp name **in the final target directory**, fsynced, then `os.replace`d to the final name; no partial final artifact ever exists. `candidate.written_atomically = true` whenever a candidate was written. On any trip the temp candidate is deleted, never renamed. Any final-path output that bypassed temp-then-rename is condition **E12** → run-level INVALID_EXPERIMENT (audited, TC-13).

## 7. Private per-run temporary storage (INV-11)

- Template: `workspace/.tmp/<run_id>/` (templated prefix only; no document-derived content in the name, INV-13).
- Created at run start; removed at dispose; on crash retained with `RETAINED_FOR_CRASH_EVIDENCE` plus a content manifest (paths, sizes, sha256s).
- `reused_across_documents` is always **false**; discovery of reuse or of a pre-existing temp dir for a live run id is condition **E07** → run-level INVALID_EXPERIMENT (audited, TC-14).
- Determinism reruns start from a clean temp state and must reproduce candidate hashes modulo `intentionally_variable_fields_declared` (INV-19).

## 8. No-network evidence (INV-12)

- **Mechanism (frozen)**: a Python audit hook (`sys.addaudithook`) installed by the harness before the worker imports, hard-failing on any `socket.*` / `urllib.Request` event; method recorded as `SOCKET_AUDIT` with `ENVIRONMENT_GUARD` noted. Evidence ref records hook-active flag, run window, event count (must be 0).
- **Declared coverage limitation (honest)**: the hook observes the worker process only. Native children (poppler `pdftotext`/`pdftoppm`/`pdfinfo`) cannot be audit-hooked without installs, and sampling tools would be probabilistic, not proof. Child-process coverage is therefore recorded in the evidence ref as `NOT_ACHIEVABLE_WITHOUT_INSTALL`; the run-level no-network claim is scoped to the audited process. Any observed socket event anywhere in the audited scope → abort run → **E06**.
- Fail closed: a run without recorded no-network evidence may not yield ACCEPT (INV-12; also enforced by `RECEIPT-SCHEMA.json` requiring `VERIFIED_NO_NETWORK` for ACCEPT/REVIEW/NOT_VERIFIABLE dispositions). Gate A / lane 06 decides whether the scoped evidence suffices; lane 05 does not assume it away.

## 9. Redaction (INV-13)

Refusal messages and human-readable summaries use frozen templated reason families plus page/region/object identifiers only; raw document text is never echoed into refusals, notes, or summaries. The CDRR itself is the evidence record and legitimately stores extracted text (per `CDRR-SCHEMA.json` note). Temp paths, receipt fields, and render filenames carry ids only. Template-family conformance is diff-checked mechanically at closure.

## 10. Retention and access

- Preserved per document run (ASSIGNMENT journey step 7): immutable original at its sealed path (never copied over, never edited), candidate, operation plan, CDRR, gate/verifier records, render PNGs of original and candidate pages, receipts — under `outputs/runs/<run_id>/` until experiment close, then hashed into `FINAL-MANIFEST`.
- Deleted: private temp state only (or crash-retained per §7). Nothing is uploaded, exported, or made network-accessible. Failed attempts and budget-tripped runs keep their receipts (INV-09; E08/E11 guards).

## 11. Dependency provenance

Only pre-installed tools are used; none may be installed (FACT: bundling per `ENVIRONMENT-INVENTORY.md` — bundled Python 3.12.14, reportlab 4.4.9, pypdf 6.10.0, pdfplumber 0.11.9, Pillow 12.3.0, poppler `pdftotext` 26.09.0, `pdftoppm`/`pdfinfo` 26.05.0; qpdf/mutool/gs absent and unused). Every receipt records actual tool name + version + provenance ref (INV-07/INV-14). Tool **roles and independence declarations are owned by lane 04 `TOOLCHAIN.json`**; if that file is absent, dependent gates are `NOT_EXERCISED` (fail closed, per lane 01 §10) — never PASS by assumption.

## 12. Known limitations and unknowns (preserved, not hidden)

1. OBJECT_COUNT, CPU_SECONDS, and OUTPUT_BYTES baselines are UNKNOWN in this packet; limits are derived or tripwire-valued; first runs must record actuals.
2. Timings are a single bounded observation on one Mac; headroom, not benchmarks, is the safety argument.
3. No-network evidence covers the worker process only (§8); child-process coverage is a recorded gap pending lane 06/Gate A adjudication.
4. Post-hoc G9 FAIL maps to PR-14 NOT_VERIFIABLE under the frozen lane 01 rules (§5); surfaced as-is.
5. Tool-version tension between `ENVIRONMENT-INVENTORY.md` and `FIXTURE-MANIFEST.json` is recorded, unresolved here (§2).
6. Budgets cover exactly the sealed slice + mutants + harness probes; they assert nothing about arbitrary PDFs.

## 13. Mechanical validation checklist (executable locally by Main)

1. `python3 -c "import json;json.load(open('BUDGETS.json'));json.load(open('TRIP-CASES.json'))"` — both parse.
2. `BUDGETS.budgets[].budget_id` set is exactly `{PAGE_COUNT, OBJECT_COUNT, FILE_BYTES, PIXELS, CPU_SECONDS, WALL_SECONDS, TEMP_STORAGE_BYTES, OUTPUT_BYTES}` (equals the `RECEIPT-SCHEMA.json` budgets enum).
3. Every budget has `limit`, `unit`, `comparison == "<="`, non-empty `measured_on`.
4. For each budget with `baseline.status` in `{MEASURED, DERIVED, DERIVED_FROM_COMPONENTS}`: `limit > baseline.observed_max_in_packet`; for `MEASURED`: `limit >= 2 * observed_max_in_packet`.
5. `frozen_constants`: `1275 * 1650 == 2103750`; `render_dpi == 150`; `page_box_pt == [612.0, 792.0]`.
6. Every `trip_cases[]` entry has `expected.original_state == "UNCHANGED_HASH_REVERIFIED"`, a present receipt, and `candidate_state` in `{NO_CANDIDATE_EVER_CREATED, DISCARDED_AT_TEMP_NEVER_PUBLISHED}`.
7. Every `trip_cases[].target_budget_id` is in the 8-id set, or the case kind is an audit/HST case citing an E-condition id in `{E06, E07, E12, E15}`.
8. `disposition_mapping` cites only existing lane 01 rule ids (`PR-08`, `PR-14`) and the refusal family `RESOURCE_BUDGET_EXCEEDED` present in the `RECEIPT-SCHEMA.json` `RefusalFamily` enum; `BUDGET_TRIP_BEFORE_GATE` present in `NotExercisedReasonCode`.
9. No network, install, or absolute out-of-workspace path appears in either JSON body.


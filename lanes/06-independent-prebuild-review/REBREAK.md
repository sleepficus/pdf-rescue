# RESULT.md — lane-06-rebreak · corrected Gate A independent review (seat-01, task-01)

Date: 2026-09-29 · Review-only re-break over the supplied sealed packet. No edits, no installs, no network, no lane content reopened. Labels: **FACT** = read directly from supplied inputs; **INFERENCE** = derived by applying frozen rules.

VERDICT: READY_FOR_VERTICAL_SLICE

## 1. Basis of verdict

**FACT** — all six corrections required by the prior NOT_READY verdict are present and evidenced in the corrected packet:

1. **SEALED.md F05 superseded (doc-only)** — the supplied `L03-SEALED.md` F05 line now reads the 64-hex value `888e283dca1174834cae8bc62ea45ca56435ed92cbb4b54f0b200f4fda3437ef`, textually identical to `FIXTURE-MANIFEST.json` (verified character-for-character by this seat from the packet); `GATE-A-MECHANICAL-CHECKS.json` GA-01/GA-02 PASS (`sealed_rows=14 manifest_rows=14`); sealed bytes untouched (PREBUILD-GATE `fixture_integrity`).
2. **Vocabulary mappings frozen** — `PREBUILD-GATE.json` contains non-empty `gate_id_map` (incl. the G8↔G10_ACTIVE, G9↔G11, G10↔G09 transposition; G08_ACROFORM_ROUNDTRIP and G12 out-of-predicate), `class_map` (BENIGN = TEXT_NATIVE_SINGLE_COLUMN + empty-plan predicate; UNRESOLVED = UNKNOWN + CONSERVATIVE_PARSER_FAILURE), `refusal_family_map`, `operation_name_map` (10-entry bijection), `delta_type_map` (all 12 lane-01 ids; lossy-echo authority rule); ESC-01 detection pass frozen `decisive=false`. GA-04 PASS. This seat re-verified the maps against the frozen L01/L02/L03 enums — they resolve.
3. **Three disambiguations frozen** — `G6_REQUIRED` (vacuous PASS; NOT_EXERCISED still blocks via PR-08), `G5_STRUCTURE_TREE` (every candidate carries a structure tree via OP_STRUCTURE_TAGS; C2 failure ⇒ G5 NOT_EXERCISED ⇒ NOT_VERIFIABLE via PR-08), `BENIGN_ZERO_OPERATIONS` (B01/B02 zero ops; metadata normalization ⇒ E15). GA-05 PASS.
4. **L04 §5 checklist + C1 + C3 executed and recorded** — `PREBUILD-GATE.toolchain_check.runtime` matches `ENVIRONMENT-INVENTORY.md` exactly (incl. poppler 26.09.0 / 26.05.0 skew; absences recorded, none installed); C1 PASS (`pdfminer.six` `20251230` imported); C3 PASS (`L04-C3-VALIDATION.json`: stdlib-only import audit, 14/14 scans, `C3-MANIFEST-HASH-DIFF` clean); C2 recorded `PENDING_POST_BUILD_FAIL_CLOSED`.
5. **Schema validation honestly recorded** — `PREBUILD-GATE.schema_validation` = `NOT_EXERCISED_REAL_VALIDATOR_UNAVAILABLE` (jsonschema ABSENT, ajv ABSENT, install NONE); fallback stdlib validator PASS 45/0 on 6 positive + 4 deliberately broken fixtures (`L02-VALIDATION.txt`).
6. **No-network scoping + version adjudication recorded** — `no_network_decision` = SCOPED_ACCEPTANCE (worker socket-audit evidence; Poppler-child gap disclosed; mandatory receipt disclosure; claim limit stated); `version_tension_adjudication` = ADJUDICATED (sealed 3.12.7/5.0.1/6.14.2 vs runtime 3.12.14/4.4.9/6.10.0; sealed bytes authoritative; mutation checks target spec semantics, not regeneration-byte identity). TC-09 corrected to `OTHER_RECORDED` in the supplied `L05-TRIP-CASES.json` (GA-15 PASS).

**FACT** — `GATE-A-MECHANICAL-CHECKS.json`: 15/15 checks PASS (GA-01…GA-15), scope statement preserves lane 06 as the independent readiness authority.

**Seat-verified arithmetic (independent of the receipts)** — 1275×1650 = 2,103,750; MEASURED limits ≥ 2× observed (8 ≥ 2×4; 204,800 ≥ 13,938); DERIVED limits exceed baselines (64,000,000 > 16,830,000; 600 > 10; 104,857,600 > 2,000,000); budget-id set equals the `RECEIPT-SCHEMA.json` budgets enum; disposition mapping cites only existing PR-08/PR-14; `RESOURCE_BUDGET_EXCEEDED` and `BUDGET_TRIP_BEFORE_GATE` exist in the receipt enums; 14 trip cases, each with `UNCHANGED_HASH_REVERIFIED`, receipt present, candidate never published.

**INFERENCE** — the remaining unproven items are each fail-closed and cannot manufacture a false PASS downstream: (a) full Draft-2020-12 validation NOT_EXERCISED → schema-invalid records are blocked at closure (INV-16/INV-24); (b) C2 pending post-build → failure yields G5 NOT_EXERCISED ⇒ NOT_VERIFIABLE via PR-08, never a false ACCEPT; (c) runtime trip execution NOT_EXERCISED → trip semantics are frozen fail-closed (zero published candidate bytes, INV-01 re-verify, atomic receipts).

**INFERENCE** — no circular/shared decisive path: builder = reportlab 4.4.9 + pypdf 6.10.0 (writer, object surgery, frozen planning extractor; pypdf banned for verifier-decisive use); verifier lineages = POPPLER (internal pairing prohibited), PDFMINER_SIX (C1-resolved), OS_UTIL, HARNESS, VERIFIER_STDLIB (C3-accepted). Expected dispositions carry the pre-builder independence guarantee (`L03-EXPECTED-DISPOSITIONS.independence_guarantee`).

**VERDICT meaning** — this authorizes Main to begin Wave B (lanes 07–09) under the conditions in §6. It is not a prediction of success; the final run status must still be derived honestly from actual outcomes.

**Seat limitations (honest)** — this seat reviewed the packet only; it did not re-run `shasum` over fixture files (fixtures are not in the seat packet) — F05 hash equality was verified textually (SEALED.md line vs manifest value) plus GA-01/GA-02/L03-VALIDATION/C3 hash-diff evidence; no validators or scanners were executed by this seat.

## 2. Preserved disclosed limitations (explicit, not silently upgraded)

1. **Full Draft-2020-12 validation is NOT_EXERCISED**: neither jsonschema nor Ajv is installed and installs are forbidden. The lane-owned stdlib fallback validator passed its positive and deliberately broken fixtures. No draft-2020-12 conformance is claimed anywhere.
2. **C2 structure-tree traversal is a post-build probe**: the frozen rule requires every candidate to carry a structure tree; C2 failure makes G5 NOT_EXERCISED and therefore NOT_VERIFIABLE via PR-08.

## 3. Gate A requirement table

| Req | Item | Status at re-break | Evidence |
|---|---|---|---|
| R1 | Draft-2020-12 schema validation | ACCEPTED_WITH_DISCLOSED_LIMIT — NOT_EXERCISED (fallback PASS 45/0) | PREBUILD-GATE `schema_validation`; `L02-VALIDATION.txt` |
| R2 | Fixture hash/size/page integrity | PASS | GA-01; `L03-VALIDATION.txt` (ALL CHECKS PASSED); `C3-MANIFEST-HASH-DIFF` PASS |
| R3 | Sealing table == manifest | PASS (corrected) | supplied `L03-SEALED.md` F05 line = manifest `888e283d…da3437ef` (64 hex, seat-verified); GA-02 |
| R4 | Expected dispositions cover id set | PASS | GA-03 `missing=[] extra=[]`; L03-VALIDATION id-set checks |
| R5 | Tool import/version checklist | PASS | PREBUILD-GATE `toolchain_check.runtime` == ENVIRONMENT-INVENTORY.md; absences recorded, no installs |
| R6 | C1 pdfminer.six resolution | PASS (20251230) | PREBUILD-GATE `toolchain_check.C1`; resolves L04 CONDITIONAL roles |
| R7 | C2 structure-tree probe | PENDING_POST_BUILD_FAIL_CLOSED (by design) | PREBUILD-GATE `toolchain_check.C2`; fail path ⇒ PR-08 NOT_VERIFIABLE |
| R8 | C3 verifier-scanner acceptance | PASS | `L04-C3-VALIDATION.json` (status PASS); GA-06 |
| R9 | Per-gate independence completeness | CONDITIONAL_POST_BUILD, acceptable to build | `L04-DEPENDENCY-SPIKE.md` §3; G1/G6 conditions now supported by C1+C3; G5 awaits C2; fail-closed rule intact |
| R10 | Budgets parse + arithmetic | PASS (static; seat-recomputed) | `L05-BUDGETS.json`; GA-07…GA-10 |
| R11 | Trip-case coverage + fail-closed protocol | PASS (static); runtime NOT_EXERCISED | `L05-TRIP-CASES.json` (14 cases; TC-09 corrected); GA-11/GA-12/GA-15 |
| R12 | No-network scoping decision | RECORDED (scoped acceptance) | PREBUILD-GATE `no_network_decision`; `L05-SAFETY-SPEC.md` §8 |
| R13 | Version-tension adjudication | PASS | PREBUILD-GATE `version_tension_adjudication` |
| R14 | Cross-lane vocabulary mappings | PASS (seat-verified vs L01/L02/L03 enums) | PREBUILD-GATE five maps; GA-04 |
| R15 | G6/G5/B01-B02 disambiguations | PASS | PREBUILD-GATE `disambiguations`; GA-05 |

## 4. Prior contradictions X-01 … X-11

| ID | Prior severity | Status | Evidence in corrected packet |
|---|---|---|---|
| X-01 | BLOCKER | CLOSED | `gate_id_map` frozen incl. transposition; G08/G12 out-of-predicate; ESC-01 `decisive=false` |
| X-02 | BLOCKER | CLOSED | SEALED.md F05 line now equals manifest hash; GA-01/GA-02 PASS; bytes untouched |
| X-03 | MAJOR | CLOSED | `class_map` (BENIGN predicate; UNRESOLVED fully pinned) |
| X-04 | MAJOR | CLOSED | `refusal_family_map` incl. R04 evidence-specific alternatives |
| X-05 | MAJOR | CLOSED | `operation_name_map` bijection + `delta_type_map` with lossy-echo authority rule |
| X-06 | MAJOR | CLOSED | `BENIGN_ZERO_OPERATIONS`; metadata normalization ⇒ E15 |
| X-07 | MAJOR | ACCEPTED_WITH_DISCLOSED_LIMIT | NOT_EXERCISED recorded per the sanctioned OR-branch; fallback PASS; installs forbidden; fail-closed at closure (INV-16/INV-24) |
| X-08 | MAJOR | CLOSED | `no_network_decision` recorded with mandatory receipt disclosure of the child-process gap |
| X-09 | MINOR | CLOSED | `version_tension_adjudication`; stale L04 “BUDGETS.json not in this packet” parenthetical superseded by the Gate-A ledger (in-file text residual, non-blocking) |
| X-10 | MINOR | CLOSED | TC-09 now `OTHER_RECORDED` in supplied TRIP-CASES.json; GA-15 PASS; `tc09_correction` recorded |
| X-11 | MINOR | CLOSED | C1 PASS (`pdfminer.six` 20251230); license facts remain UNKNOWN-UNVERIFIED by design, no waiver (per frozen fix) |

Prior conflicting outcomes CO-1…CO-5 are all resolved: CO-1/CO-2 by `gate_id_map`; CO-3 by `G6_REQUIRED`; CO-4 by `G5_STRUCTURE_TREE`; CO-5 by the SEALED.md F05 correction.

## 5. New findings from this re-break

No new BLOCKER or MAJOR contradiction found. Two minor, non-blocking observations:

- **N-01 (SUPERSEDED_TEXT_RESIDUAL, MINOR)** — `L03-EXPECTED-DISPOSITIONS.json` F01 note (“G6 may be NOT_EXERCISED … ACCEPT may still stand”) and F02/F04 `gates_not_exercised=["G6"]` remain in-file but are superseded by `PREBUILD-GATE.disambiguations.G6_REQUIRED` (G6 runs vacuously on every in-scope class; NOT_EXERCISED still blocks via PR-08). Expected dispositions are unchanged (ACCEPT under both readings; only the recorded G6 status differs). Implementers must follow the L01 matrix + PREBUILD-GATE, not the in-file L03 notes.
- **N-02 (HYGIENE, MINOR)** — `L04-C3-VALIDATION.json` embeds absolute sealing-machine paths in scan records. No checked rule prohibits this (GA-14 scope = correction artifacts; SAFETY-SPEC §13.9 scope = L05 JSONs); the paths are provenance, not external action, and INV-13 (document-text redaction) is not implicated.

## 6. Wave B conditions (binding)

1. Run the C2 post-build probe (frozen one-page tagged candidate, pdfminer.six-only path); on failure G5 NOT_EXERCISED ⇒ NOT_VERIFIABLE via PR-08 — no waiver.
2. Every candidate carries a structure tree via OP_STRUCTURE_TAGS so G5's second derivation is attempted.
3. G6 REQUIRED runs on every in-scope class; vacuous PASS with empty inventories from both independent readers; L03 F01/F02/F04 G6 notes are superseded.
4. B01/B02 receive zero operations; metadata normalization is not a frozen operation (E15 otherwise).
5. ESC-01 detection-pass results recorded with `decisive=false`; conflicts route to PR-03.
6. Lane-02 receipt delta values are lossy echoes; the authoritative lane-01 delta id, anchor, scope, and magnitude stay in the operation evidence references.
7. Any `VERIFIED_NO_NETWORK` receipt cites worker socket-audit `evidence_ref` and explicitly discloses unaudited Poppler-child coverage; claim is scoped to the audited worker; any observed network event ⇒ E06 INVALID_EXPERIMENT.
8. Receipts cite actual runtime versions (Python 3.12.14 / reportlab 4.4.9 / pypdf 6.10.0 / pdfplumber 0.11.9 / pdfminer.six 20251230 / pdftotext 26.09.0 / pdftoppm+pdfinfo 26.05.0 skew); mutation checks verify MUTATION-SPECS `exact_edit` + `expected_text_signature` semantics, never sealed-byte regeneration identity.
9. Full Draft-2020-12 validation remains NOT_EXERCISED; schema-invalid records are blocked at closure (INV-16/INV-24); no validator-conformance claim.
10. Runtime trip execution (TC-01…TC-14, NTC-01…NTC-03) is exercised in Wave B/C; G9 requires per-run harness observation; a post-hoc G9 FAIL maps to PR-14 NOT_VERIFIABLE (no invented harsher rule).
11. INV-08 everywhere: NOT_EXERCISED is never PASS; ERROR is treated worse than FAIL.

## 7. REBREAK.json

```json
{
  "artifact": "REBREAK.json",
  "seat_id": "seat-01",
  "stage": "lane-06-rebreak",
  "date": "2026-09-29",
  "verdict": "READY_FOR_VERTICAL_SLICE",
  "verdict_meaning": "Authorizes Main to begin Wave B (lanes 07-09) under wave_b_conditions; not a success prediction.",
  "basis": {
    "prior_corrections_recorded": 6,
    "mechanical_checks": "15/15 PASS (GATE-A-MECHANICAL-CHECKS.json GA-01..GA-15)",
    "new_blocking_contradictions": 0,
    "fail_closed_remaining_items": [
      "full Draft-2020-12 validation NOT_EXERCISED",
      "C2 structure-tree probe pending post-build (failure => G5 NOT_EXERCISED => NOT_VERIFIABLE via PR-08)",
      "runtime trip execution NOT_EXERCISED"
    ]
  },
  "prior_findings": {
    "X-01": "CLOSED",
    "X-02": "CLOSED",
    "X-03": "CLOSED",
    "X-04": "CLOSED",
    "X-05": "CLOSED",
    "X-06": "CLOSED",
    "X-07": "ACCEPTED_WITH_DISCLOSED_LIMIT",
    "X-08": "CLOSED",
    "X-09": "CLOSED",
    "X-10": "CLOSED",
    "X-11": "CLOSED"
  },
  "new_findings": [
    {"id": "N-01", "severity": "MINOR_NON_BLOCKING", "kind": "SUPERSEDED_TEXT_RESIDUAL", "summary": "L03-EXPECTED-DISPOSITIONS.json F01 G6 note and F02/F04 gates_not_exercised=['G6'] superseded by PREBUILD-GATE disambiguations.G6_REQUIRED; dispositions unchanged."},
    {"id": "N-02", "severity": "MINOR_NON_BLOCKING", "kind": "HYGIENE", "summary": "L04-C3-VALIDATION.json embeds absolute sealing-machine paths; provenance only; no rule violated."}
  ],
  "wave_b_conditions": [
    "C2 post-build probe fail-closed (G5 NOT_EXERCISED => NOT_VERIFIABLE via PR-08) on failure",
    "every candidate carries a structure tree via OP_STRUCTURE_TAGS",
    "G6 REQUIRED vacuous-PASS rule; L03 F01/F02/F04 G6 notes superseded",
    "B01/B02 zero operations; metadata normalization => E15",
    "ESC-01 detection pass decisive=false; conflicts => PR-03",
    "lane01 delta id/anchor/scope/magnitude authoritative in evidence refs; lane02 echoes lossy",
    "VERIFIED_NO_NETWORK receipts must cite worker audit evidence and disclose unaudited Poppler children; observed network event => E06",
    "receipts record actual runtime versions; mutation checks target spec semantics + expected_text_signature, not byte identity",
    "Draft-2020-12 stays NOT_EXERCISED; schema-invalid records blocked at closure (INV-16/INV-24)",
    "runtime trip execution in Wave B/C; post-hoc G9 FAIL => PR-14 NOT_VERIFIABLE",
    "INV-08: NOT_EXERCISED never PASS; ERROR worse than FAIL"
  ]
}
```


# PREBUILD-VERDICT.md — lane 06 independent prebuild breaker (seat-01, task-06)

Date (frozen constant): 2026-09-29. Basis: sealed lane 01–05 packets only. No repairs, installs, or network; no lane content modified.

## Verdict

**NOT_READY**

## Basis

FACT: the frozen substance is close to buildable. Lane 01's `dispose()` is total and validator-proven (L01-VALIDATION.txt, 64/64); lane 03 is sealed and hash/size/page-verified against its machine manifest (L03-VALIDATION.txt), with expected dispositions authored before any builder existed; lane 05's budgets/trip protocol is mechanical and internally consistent; lane 04 is fail-closed. No circular proof was found (see audit below).

INFERENCE: the verdict is NOT_READY because applying the frozen rules verbatim to the same recorded events yields conflicting dispositions, and one sealing-evidence artifact contradicts the machine manifest. Conflicting outcomes produced:

1. Gate-id transposition (no mapping artifact exists in the packet). Event "G9 FAIL": lane01/03 reading = budget/no-network, no PR maps G9 FAIL, so PR-14 => NOT_VERIFIABLE (L05-SAFETY-SPEC S5 records this honestly); lane02 reading = G09_INDEPENDENT_RENDER_INK => lane01 PR-11 => REFUSE. Event "G10 FAIL": lane01/03 = render => PR-11 REFUSE; lane02 G10_ACTIVE_CONTENT_SECURITY_SCAN (= lane01 G8) => PR-04 REFUSE via a different rule/provenance. lane02 G08_ACROFORM_ROUNDTRIP has no lane01 counterpart; lane01 G8 has no lane02 number. L05-BUDGETS gate_mapping freezes only G11<->G9 and G09<->G10. INV-20's mechanical derivation audit cannot pass through this seam.
2. SEALED.md vs FIXTURE-MANIFEST.json, F05-article.pdf (FACT): SEALED.md line is 63 hex chars (`...0b2004fda3437ef`); the manifest (stated machine authority; validate.py PASS against the files) is 64 (`...0b200f4fda3437ef`). SEALED.md itself requires `shasum -a 256 fixtures/*.pdf` to reproduce its table; it cannot. Two different hashes asserted for one sealed artifact.
3. G6 REQUIRED vs L03 note: lane01 makes G6 REQUIRED for every in-scope class and PR-08 turns a REQUIRED NOT_EXERCISED into NOT_VERIFIABLE; L03-EXPECTED-DISPOSITIONS F01 note says "G6 may be NOT_EXERCISED ... ACCEPT may still stand." Same run: ACCEPT (L03 reading) vs NOT_VERIFIABLE (lane01 reading).
4. G5 second derivation: lane04 freezes C2's fail path as "NOT_DERIVABLE => G5 NOT_EXERCISED for affected documents"; G5 is REQUIRED for all in-scope classes => PR-08 NOT_VERIFIABLE. L03 expects ACCEPT for F02/F04 whose frozen expected plans add no structure tags, so the structure-based derivation is not derivable and lane04's fail-closed reading fires. Same candidate: ACCEPT (L03) vs NOT_VERIFIABLE (lane01+lane04).
5. Class/refusal/delta vocabularies do not interoperate without a frozen mapping: lane02's class_label enum cannot express BENIGN (the CDRR disposition echo cannot record the engine's class input, stressing INV-20); refusal families appear in three vocabularies (`refuse/active` vs `ACTIVE_CONTENT_OR_JAVASCRIPT` vs `"active-content"`); lane01's 12 delta types vs lane02's 11 are non-isomorphic (METADATA_ONLY, DUPLICATE_SUPPRESSION, NO_TEXT_DELTA are lane02-only; LINE_END_WHITESPACE_STRIP lane01-only); L03-B02 invites "metadata normalization", which is outside lane01's frozen ten operations (INV-15/E15 would invalidate the run).

## Shared decisive path audit

Builder = reportlab 4.4.9 (writer) + pypdf 6.10.0 (object surgery, planning extractor). Verifier lineages = POPPLER (pdftotext 26.09.0, pdftoppm/pdfinfo 26.05.0), PDFMINER_SIX (pdfplumber 0.11.9 + pdfminer.six, C1-pending), OS_UTIL, HARNESS. Disjoint; pypdf banned for verifier-decisive use; POPPLER-internal pairs prohibited as independence pairs and respected (G4/G10 = pdftoppm + pdfplumber; G2 = pdfplumber + pdftotext -bbox-layout); G10's comparison extractor is frozen to PDFMINER_SIX. Expected dispositions carry an explicit pre-builder independence guarantee (L03-EXPECTED-DISPOSITIONS `independence_guarantee`). Verifier-never-repairs is enforced (INV-06/E03). No shared decisive path between builder and verifier was found; CONDITIONAL gates: G1/G6 (C1/C3), G5 (C1/C2), G9 (harness observation; BUDGETS.json now supplied).

## Budgets / trip semantics (mechanical check)

PASS on static inspection: 8 budget ids exactly equal the RECEIPT-SCHEMA budgets enum; 1275x1650 = 2,103,750; every MEASURED limit >= 2x observed max (8 >= 2x4; 204,800 >= 2x6,969); DERIVED limits exceed baselines; disposition mapping cites only existing PR-08/PR-14 and existing enum values; trip protocol is fail-closed (zero published candidate bytes, INV-01 re-verify, atomic receipts). Runtime trip execution NOT_EXERCISED. Minor: TC-09 (network trip) records refusal_family RESOURCE_BUDGET_EXCEEDED, which is not a resource-budget event; TC-13/TC-14 already use OTHER_RECORDED.

## Unproven claims (preserved UNKNOWN; NOT_EXERCISED is not PASS)

- Lane02 schemas were validated only by a stdlib fallback under Python 3.9.6 with jsonschema absent (L02-VALIDATION.txt INFO lines): draft-2020-12 semantics (oneOf/if-then/const) NOT_EXERCISED.
- C1 (pdfminer.six import/version): UNKNOWN; load-bearing — on fail, G1/G5/G6 fall closed and every in-scope disposition becomes NOT_VERIFIABLE via PR-08.
- C3 unrun; C2 requires a lane09 probe (post-build; fail-closed path defined).
- No-network evidence is worker-process-only (L05-SAFETY-SPEC S8: poppler children NOT_ACHIEVABLE_WITHOUT_INSTALL) while RECEIPT-SCHEMA requires VERIFIED_NO_NETWORK for ACCEPT/REVIEW/NOT_VERIFIABLE: a scoping decision with evidence_ref disclosure is mandatory at Gate A.
- Determinism double-generation evidence binds to reportlab 5.0.1 / pypdf 6.14.2 / Python 3.12.7, not the runtime's 4.4.9 / 6.10.0 / 3.12.14: mutant checks must target mutation-spec semantics, not sealed bytes; actual run versions must be recorded and adjudicated.
- All license facts correctly remain UNKNOWN-UNVERIFIED (no waiver invented).

## Gate A requirement ledger

| # | Requirement | Evidence path | Status now |
|---|---|---|---|
| 1 | Draft-2020-12 validation of CDRR/RECEIPT schemas | inputs/L02-VALIDATION.txt | NOT_EXERCISED (fallback validator only) |
| 2 | Fixture hash/size/page integrity vs manifest | inputs/L03-VALIDATION.txt | PASS |
| 3 | Sealing receipt table == manifest | inputs/L03-SEALED.md | FAIL (F05, 63-char hash) |
| 4 | Expected dispositions cover fixture id set | inputs/L03-EXPECTED-DISPOSITIONS.json | PASS |
| 5 | Tool import + version checklist (L04 S5) | inputs/L04-TOOLCHAIN.json; inputs/ENVIRONMENT-INVENTORY.md | NOT_EXERCISED |
| 6 | C1 pdfminer.six resolution | inputs/L04-TOOLCHAIN.json (C1) | NOT_EXERCISED |
| 7 | C2 structure-tree probe | inputs/L04-TOOLCHAIN.json (C2) | NOT_EXERCISED (post-build, fail-closed) |
| 8 | C3 verifier-scanner acceptance | inputs/L04-TOOLCHAIN.json (C3) | NOT_EXERCISED |
| 9 | Per-gate independence completeness | inputs/L04-DEPENDENCY-SPIKE.md S3 | NOT_EXERCISED (G2/G3/G4/G7/G8/G10 MET; G1/G5/G6 CONDITIONAL) |
| 10 | Budgets parse + arithmetic (SAFETY-SPEC S13) | inputs/L05-BUDGETS.json; inputs/L05-TRIP-CASES.json | PASS (static); runtime NOT_EXERCISED |
| 11 | Trip-case coverage + fail-closed protocol | inputs/L05-TRIP-CASES.json | PASS (static) |
| 12 | No-network scoping decision | inputs/L05-SAFETY-SPEC.md S8; inputs/L02-RECEIPT-SCHEMA.json | NOT_EXERCISED (decision pending) |
| 13 | Version-tension adjudication | inputs/ENVIRONMENT-INVENTORY.md vs inputs/L03-FIXTURE-MANIFEST.json | NOT_EXERCISED |
| 14 | Cross-lane vocabulary mapping frozen | none exists | FAIL (must be created in PREBUILD-GATE.json) |
| 15 | G6 / G5 / B02 rule disambiguations frozen | L03 notes vs L01/L04 rules | FAIL (one-line freezes required) |

## Smallest consolidated correction (no lane substance reopened)

1. Supersede the SEALED.md F05 line with the manifest/file hash (documentation supersede only; sealed bytes untouched; manifest remains authority).
2. Freeze in PREBUILD-GATE.json the mapping tables listed in CONTRADICTIONS.json: gate_id_map (including the G8<->G10_ACTIVE, G9<->G11, G10<->G09 transposition; G08_ACROFORM_ROUNDTRIP and G12 out-of-predicate), class_map (BENIGN == TEXT_NATIVE_SINGLE_COLUMN + empty plan; REFUSE_* == UNSUPPORTED + refusal_family; UNRESOLVED == UNKNOWN + CONSERVATIVE_PARSER_FAILURE), refusal_family_map, operation_name_map (OP_* == bare names), delta_type_map; ESC-01 detection-pass results recorded with decisive=false.
3. Freeze three one-line rules: REQUIRED G6 runs on every in-scope class and may record vacuous PASS (L03 F01/F02/F04 notes superseded); every candidate carries a structure tree via OP_STRUCTURE_TAGS so G5's second derivation is derivable, else G5 NOT_EXERCISED => NOT_VERIFIABLE via PR-08; B01/B02 receive zero operations (metadata normalization is not a frozen operation; E15 otherwise).
4. Run the L04 S5 checklist plus C1 and C3 at Gate A; record results verbatim in PREBUILD-GATE.json; record C2 as pending with its fail-closed consequence.
5. Re-validate both lane02 schemas with a real draft-2020-12 validator on the bundled runtime, or record schema-validation NOT_EXERCISED in PREBUILD-GATE.json.
6. Record the scoped no-network decision with mandatory evidence_ref disclosure of the child-process gap, and the version-tension adjudication.

RECOMMENDATION: after items 1–6 are recorded, re-dispatch lane 06; on the corrected packet the expected verdict is READY_FOR_VERTICAL_SLICE without reopening any lane's frozen content.

## Exact machine checks for Main

1. `shasum -a 256 fixtures/*.pdf` and assert all 14 equal FIXTURE-MANIFEST.json values (also establishes F05's true hash; only the uncorrected SEALED.md line should mismatch).
2. `python3 -c "import reportlab,pypdf,pdfplumber,PIL;print(reportlab.Version,pypdf.__version__,pdfplumber.__version__,PIL.__version__)"` must print 4.4.9 6.10.0 0.11.9 12.3.0, else STOP with NOT_READY (L04 S5).
3. `python3 -c "import pdfminer;print(pdfminer.__version__)"` — C1; on fail record G1/G5/G6 fall-closed.
4. `pdftotext -v; pdftoppm -v; pdfinfo -v` — record versions including the 26.09.0/26.05.0 skew.
5. `command -v qpdf mutool gs` — expect no output.
6. On the bundled runtime: `python3 -c "import jsonschema"`; if importable, validate L02-CDRR-SCHEMA.json and L02-RECEIPT-SCHEMA.json against lane02's own sample/broken fixtures; else record NOT_EXERCISED.
7. Script SAFETY-SPEC S13 checks 1–9 against L05-BUDGETS.json and L05-TRIP-CASES.json (parse; id-set equality with the receipt enum; limit arithmetic; frozen constants; trip-case expectations; PR-id/enum citations; no network/installs/absolute paths).
8. Assert PREBUILD-GATE.json contains non-empty gate_id_map, class_map, refusal_family_map, operation_name_map, delta_type_map, and the three disambiguations.
9. Re-dispatch lane 06 for re-break.

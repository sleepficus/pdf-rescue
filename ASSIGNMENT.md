# ZCode GLM assignment - online PDF reconstruction guarded build

Date: 2026-09-29

## Objective

Turn the completed investigation into the smallest honest working experiment:

> A deliberately ugly, text-native PDF goes in; a visibly cleaner PDF comes
> out; mechanical evidence proves that material text, numbers, reading order,
> page count, page boundaries, and visible meaning were not silently changed.

This is a **guarded local experiment**, not a production product. The prior
investigation ended `NOT_READY_FOR_BUILD` because the protocol, fixtures,
oracle, dependency choices, and safety controls were not frozen. Resolve those
items first. Do not treat this assignment as permission to waive them.

## Authoritative inputs

Read every file under `inputs/` before delegating. In conflicts, use this order:

1. `inputs/FINAL-RECONCILIATION.md`
2. this assignment
3. `inputs/MAIN-GLM-SYNTHESIS.md`
4. the remaining receipts and run card

The `inputs/` directory is read-only. Preserve its hashes.

## Hard boundaries

- Work only inside this project directory.
- Do not read unrelated local files or prior PDF Workbench source.
- Do not use real, private, medical, financial, or downloaded PDFs.
- Generate only synthetic, rights-safe fixtures inside this project.
- No network calls, provider calls, uploads, installs, package-manager writes,
  system changes, services, deployment, or modification of another project.
- Use only dependencies already present. Record missing tools; do not install.
- Original fixture PDFs are immutable after sealing.
- A verifier may never repair the candidate it evaluates.
- `NOT_EXERCISED` is not `PASS`; unknown is not success.
- If a prerequisite cannot be made mechanical, stop with `NOT_READY` rather
  than inventing a favorable rule.
- No self-repair, autonomous retries outside the frozen test plan, or expansion
  into OCR, scans, inferred forms, signatures, encryption, XFA, JavaScript,
  active content, complex RTL/bidi, or an online service.

## Ten-agent execution plan

Spawn exactly ten named, non-overlapping subagents. Run no more than three at
once. Every subagent writes only to its exact `lanes/<name>/` directory. The
main ZCode agent is the sole integrator and writes `workspace/`, `outputs/`,
and `receipts/`. No subagent may edit another lane or the integrated workspace.

### Wave A - freeze the missing pre-build contract

1. `01-protocol-disposition`
   - Freeze material-element definitions, gate statuses, class-by-gate matrix,
     disposition precedence, human-confirmation replay, and six ambiguous
     scenarios.
   - Output: `PROTOCOL.md`, `DISPOSITION-SPEC.json`, `SCENARIOS.json`.

2. `02-cdrr-receipts`
   - Freeze the Common Document Reconstruction Record, operation record,
     verifier record, run receipt, and `NOT_EXERCISED`/`ERROR` semantics.
   - Output: `CDRR-SCHEMA.json`, `RECEIPT-SCHEMA.json`, `INVARIANTS.md`.

3. `03-fixtures-oracles`
   - Specify and generate a deterministic synthetic fixture/oracle pack for
     exactly eight text-native development documents plus refusal and benign
     controls. Freeze seeds before generation. No real PDFs.
   - Output: fixture sources/PDFs, `FIXTURE-MANIFEST.json`,
     `EXPECTED-DISPOSITIONS.json`, `ORACLE-NOTES.md`.

4. `04-dependencies-independence`
   - Inspect only already-installed tools. Select the smallest permissive
     builder path, independent second extractor, and independent renderer.
     Demonstrate that builder and verifier do not share the same decisive path.
   - Output: `DEPENDENCY-SPIKE.md`, `TOOLCHAIN.json`, `LICENSE-NOTES.md`.

5. `05-safety-budgets`
   - Freeze measured local budgets and trip behavior for page count, object
     count, bytes, pixels, CPU/wall time, temp storage, and output size. Define
     private temp lifecycle, no-network evidence, redaction, and atomic output.
   - Output: `SAFETY-SPEC.md`, `BUDGETS.json`, `TRIP-CASES.json`.

6. `06-independent-prebuild-review`
   - Read lanes 01-05 only after they finish. Attempt to produce conflicting
     outcomes from their rules, find circular/shared-path proofs, and decide
     `READY_FOR_VERTICAL_SLICE` or `NOT_READY` with exact reasons.
   - Output: `PREBUILD-VERDICT.md`, `CONTRADICTIONS.json`.

### Mandatory gate A

The main agent must validate schemas, fixture hashes, expected dispositions,
tool availability, independence, and safety rules. Write
`outputs/PREBUILD-GATE.json`.

If Gate A is not exactly `READY_FOR_VERTICAL_SLICE`, stop. Do not spawn Waves B
or C. Write honest results and set final status `NOT_READY`.

### Wave B - bounded implementation, only after Gate A passes

7. `07-intake-extract`
   - Implement immutable intake, byte/MIME checks, Phase-0 refusal scan,
     canonical page/text extraction, and CDRR production for the eight sealed
     text-native fixtures.
   - Output code/tests only in this lane.

8. `08-plan-apply`
   - Implement only the frozen allowed tidy operations: spacing, alignment,
     typography with glyph verification, declared line-end hyphenation,
     repeated header/footer normalization, structure tags, reading order,
     outline/bookmarks, and verified internal navigation. Page count, page
     order, and page boundaries are immutable.
   - Output code/tests only in this lane.

9. `09-independent-verify`
   - Implement independent extraction/render comparison, text and numeric
     lexeme identity, reading-order checks, page geometry checks, visible/text
     agreement, expected-delta reconciliation, and deterministic disposition.
   - It must detect seeded deletion, transposition, wrong reading order,
     numeric reassignment, bookmark loss, and hidden-text poison.
   - Output code/tests only in this lane.

The main agent integrates lanes 07-09 into `workspace/` only after reviewing
their diffs and preserving provenance. Prefer a simple Python package and CLI;
do not create a platform or web service.

### Wave C - independent closure

10. `10-closure-breaker`
    - Read the sealed protocol/oracle pack and integrated workspace. Do not
      edit code. Run the frozen tests, mutation checks, reproducibility checks,
      no-network observation, and render every original/candidate page.
    - Output: `CLOSURE.md`, `FAILURES.json`, `RENDER-REVIEW.md`.

## Required integrated journey

For all eight development fixtures:

1. freeze and hash the source;
2. classify and build a CDRR;
3. create an explicit operation plan;
4. render a candidate to an atomic temporary path;
5. independently verify source versus candidate;
6. mechanically derive a disposition;
7. preserve original, candidate, plan, CDRR, gate records, render PNGs, and
   receipt;
8. rerun from clean temp state and prove deterministic hashes or explain any
   intentionally variable metadata.

At least one supported fixture must be visibly improved, but visual preference
cannot override a failed meaning-preservation gate.

## Required final outputs

- `outputs/RESULTS.md`
- `outputs/STATUS.json`
- `outputs/PREBUILD-GATE.json`
- `outputs/FINAL-MANIFEST.sha256`
- `outputs/TEST-RECEIPT.md`
- `outputs/RENDER-REVIEW.md`
- `outputs/LANE-INDEX.json`
- integrated implementation under `workspace/` only if Gate A passed

Final status must be one of:

- `VERTICAL_SLICE_VERIFIED`
- `VERTICAL_SLICE_FAILED`
- `NOT_READY`
- `INVALID_EXPERIMENT`

Do not claim production readiness, installation, deployment, broad PDF
support, OCR support, or safety beyond what was directly exercised.


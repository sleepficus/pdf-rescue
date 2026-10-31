# Online PDF reconstruction — guarded vertical-slice result

Date: 2026-09-29

## Outcome

`VERTICAL_SLICE_VERIFIED`

The bounded synthetic experiment succeeded. Eight text-native fixture PDFs
were processed locally. All eight candidates matched their expected `ACCEPT`
disposition, source fixture bytes remained unchanged, two clean builds produced
identical candidate hashes, and one document (F02) showed a mechanically
measured visible spacing improvement without changing normalized text, numeric
lexemes, page count, geometry, reading order, navigation, or visible meaning.

This is not a production PDF service. It does not establish support for real,
private, scanned, OCR, signed, encrypted, XFA, JavaScript-bearing, complex
RTL/bidi, or arbitrary online PDFs.

## What was exercised

- Gate A: 15/15 mechanical checks passed after an independent re-break returned
  `READY_FOR_VERTICAL_SLICE`.
- Intake: immutable source hashing, PDF/header/inventory checks, Phase-0 refusal
  classification, text/numeric capture, and CDRR records.
- Build: deterministic cloning, a real structure tree on every development
  candidate, fixed metadata, atomic publication, and one narrowly scoped text
  operand spacing repair on F02.
- Independent verification: pdfminer/pdfplumber plus Poppler/Pillow, with no
  pypdf/reportlab import in the verifier.
- Hostile mutations: M01 deletion, M02 token transposition, M03 wrong reading
  order, M04 numeric reassignment, M05 bookmark loss, and M06 hidden-text poison
  all failed their preregistered target gates and none was accepted.
- Rendering: 19 source pages and 19 candidate pages were rendered at 120 DPI;
  eight complete side-by-side contact sheets were visually inspected.
- Reopen checks: all eight final candidates reopened with strict pypdf and
  `pdfinfo` reported the expected page counts.

## Results by fixture

| Fixture | Pages | Final disposition | Deterministic | Visible change |
|---|---:|---|---|---|
| F01 | 2 | ACCEPT | yes | none |
| F02 | 1 | ACCEPT | yes | one double-space defect reduced from 1 to 0 |
| F03 | 2 | ACCEPT | yes | none |
| F04 | 1 | ACCEPT | yes | none |
| F05 | 3 | ACCEPT | yes | none |
| F06 | 3 | ACCEPT | yes | none |
| F07 | 4 | ACCEPT | yes | none |
| F08 | 3 | ACCEPT | yes | none |

F02's maximum changed-pixel fraction was `0.0033140819964349376`, below the
frozen `0.005` limit. Every other final candidate had a zero changed-pixel
fraction.

## Provider and execution limitation

The exact `glm-5.3-flashx` Wave B route was attempted twice with no fallback or
retry beyond the explicitly authorized compact recovery. All six substantial
lane calls returned HTTP 200 with the exact requested model but no final text;
the adapter recorded `RuntimeError: provider returned no final text`. Main then
implemented the already-frozen narrow lanes, ran their unit tests, and performed
the closure checks directly. No third provider wave was spent.

Therefore the artifact behavior is verified, but this run does not claim that
the requested ten-worker ZCode execution topology completed successfully. The
provider failure is preserved as evidence rather than relabeled as worker
success.

## Safety and scope receipts

- Inputs revalidated against `INPUT-MANIFEST.sha256` at closure.
- The implementation contains no path reference to the accepted RoomKit source
  and wrote only inside this assignment directory.
- Socket `connect` and `create_connection` were blocked in the Python harness.
  Poppler children received only local paths; child-process socket coverage was
  not independently audited, so this is not production-grade network isolation.
- Nothing was installed, deployed, uploaded, or connected to a provider during
  PDF execution.

Detailed evidence: `RUN-RESULTS.json`, `MUTATION-RESULTS.json`,
`CLOSURE-CHECKS.txt`, `TEST-RECEIPT.md`, and `RENDER-REVIEW.md`.

# Lane 09 — independent verification and disposition

Implement only these files under the shared integration contract:

- `pdfslice/verifier.py`
- `pdfslice/disposition.py`
- `tests/test_verifier.py`

Required behavior:

1. No reportlab or pypdf import anywhere in these files.
2. Independent source/candidate checks for G1..G10 using pdfminer.six /
   pdfplumber, explicit Poppler executable paths, Pillow, stdlib, and the
   accepted scanner.
3. Compare source/candidate page count/order/boxes, canonical text and numeric
   lexemes, visible/text-layer agreement, reading order, tables, navigation,
   security markers, budgets, and 150-DPI render/ink regions.
4. Implement C2 using pdfminer.six low-level catalog traversal: a candidate
   lacking or exposing an unreadable structure tree makes G5 NOT_EXERCISED.
5. G6 always executes and may vacuously PASS only after pdfplumber and the
   stdlib scanner independently report empty navigation inventories.
6. Reconcile observed material deltas only against declared lane-01 expected
   delta type/scope/bounds. No verifier repair.
7. Implement the frozen PR-00..PR-14 precedence mechanically from the supplied
   disposition JSON, not from summary intuition.
8. Tests must detect seeded deletion, transposition, wrong reading order,
   numeric reassignment, bookmark loss, hidden-text poison, missing structure,
   and a clean no-op control. NOT_EXERCISED never counts as PASS.

Do not implement intake, candidate writing, CLI, or pipeline.

Keep the entire RESULT under 28,000 characters. Prefer deterministic helpers
that return honest NOT_EXERCISED/ERROR states when evidence or a tool is absent.
Return code blocks only in the shared format; do not restate the supplied
contracts.

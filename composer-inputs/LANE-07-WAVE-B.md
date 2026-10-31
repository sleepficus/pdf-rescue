# Lane 07 — intake and extraction

Implement only these files under the shared integration contract:

- `pdfslice/intake.py`
- `tests/test_intake.py`

Required behavior:

1. Immutable source hash/size/PDF-header checks and manifest agreement.
2. Conservative Phase-0 refusal scan for encrypted, signed/certified, XFA,
   JavaScript/launch/embedded/remote-target, and pending-redaction evidence.
3. Object/page inventory and canonical page extraction for F01-F08 and benign
   controls using installed tools only.
4. Stable single- versus multi-column versus table classification sufficient
   for the sealed synthetic fixtures; classifier uncertainty becomes
   UNRESOLVED, never guessed.
5. Canonical reading-order text, tokens, numeric lexemes, boxes, navigation,
   and JSON-safe evidence fields.
6. A `build_cdrr_skeleton(intake_record)` helper with every section present;
   refused sections are explicit NOT_EXERCISED with empty records.
7. Tests cover one supported fixture, every refusal family, manifest mismatch,
   numeric lexemes, and source bytes unchanged.

Do not implement planning, candidate writing, verification, CLI, or pipeline.

Keep the entire RESULT under 24,000 characters. Prefer small composable
functions and compact unittest coverage. Return code blocks only in the shared
format; do not restate the supplied contracts.

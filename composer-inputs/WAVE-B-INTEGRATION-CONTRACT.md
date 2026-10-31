# Wave B integration contract

This is a deliberately small local Python vertical slice named `pdfslice`.
Workers return code text only. Main is the sole integrator and will write and
run the integrated workspace after reviewing every result.

## Hard rules

- Never read or write outside the project workspace at runtime.
- No network, install, shell interpolation, service, upload, OCR, or real PDF.
- Source PDFs are read-only; candidate publication is temp + fsync +
  `os.replace` and is owned by Main's pipeline, not lane modules.
- Builder lineage may use installed `reportlab` and `pypdf`.
- Verifier-decisive logic must not use `reportlab` or `pypdf`; use installed
  `pdfplumber`/`pdfminer.six`, Poppler executables passed explicitly by Main,
  Pillow, stdlib, and the accepted stdlib scanner.
- JSON artifacts are deterministic: sorted keys, stable lists, no current time
  inside candidate bytes, no random ids.
- Never convert NOT_EXERCISED or ERROR to PASS.
- All returned code must be concise, typed where useful, and testable with
  stdlib `unittest` or pytest already present; no new dependency.

## Shared JSON interfaces

`inspect_document(source, manifest_entry, scanner) -> intake_record`

- keys: `document_id`, `filename`, `source_sha256`, `file_bytes`,
  `page_count`, `object_count`, `class_label` (lane-01 vocabulary),
  `refusal_family`, `status`, `pages`, `navigation`, `security_scan`,
  `runtime_versions`, `evidence`.
- each page carries stable `page_index`, boxes, rotation, canonical
  `reading_text`, `tokens`, `numeric_lexemes`, and word records with x/y boxes.
- refusal controls stop before extraction and carry no document text in the
  templated refusal summary.

`plan_document(intake_record, expected_record) -> plan`

- lane-01 operation names and delta ids are authoritative.
- every F01-F08 candidate includes `OP_STRUCTURE_TAGS`; every plan declares
  anchors, scope, and bounded expected deltas.
- B01/B02 have an empty operation list and are never rebuilt.
- refusal/UNRESOLVED records have no candidate plan.

`build_candidate(source, intake_record, plan, temp_output) -> build_record`

- source never changes; page count/order/boundaries remain identical.
- reconstruction uses deterministic base-14 fonts and fixed metadata.
- every rebuilt candidate has a real `/StructTreeRoot`, marked content/MCIDs,
  `/MarkInfo`, per-page `/StructParents`, and a ParentTree; bookmarks and
  verified internal navigation only when declared.
- output remains at the supplied temp path; no final rename.

`verify_candidate(source, candidate, intake_record, plan, tools, scanner) -> verification`

- keys: `gates` for G1..G10, `observed_deltas`, `independence`,
  `c2_structure_probe`, `no_network_scope`, `runtime_versions`.
- G6 always runs; it may vacuously PASS only after two independent empty
  inventories. G5 cannot PASS if C2 cannot derive the candidate structure.
- G7 detection runs on every in-scope class with `decisive=false` unless it
  exposes ESC-01 classifier conflict.

`derive_disposition(class_label, gates, reconciliation, disposition_spec)`
returns exactly one of ACCEPT, REVIEW, REFUSE, NOT_VERIFIABLE plus fired rule.

## Worker output format

Return one `RESULT.md`. For every proposed file use exactly:

`## FILE: relative/path.py`

followed by one fenced Python block. Include a final `## NOTES` section listing
assumptions and commands Main should run. Do not include alternate versions or
duplicate file blocks.

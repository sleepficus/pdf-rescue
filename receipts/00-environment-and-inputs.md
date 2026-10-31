# Receipt 00 — input verification and local environment probe

Date: 2026-09-29
Writer: main ZCode agent (sole integrator)

## Input hash verification

Command: `shasum -a 256 -c INPUT-MANIFEST.sha256` from the project root.

```
inputs/FINAL-MANIFEST.sha256: OK
inputs/FINAL-RECONCILIATION.md: OK
inputs/MAIN-GLM-SYNTHESIS.md: OK
inputs/RUN-CARD.md: OK
inputs/STATUS.json: OK
inputs/VERIFICATION-RECEIPT.md: OK
```

All 6 manifest entries verified. `inputs/` is treated as read-only for the rest
of the run and will be re-checked before Gate A.

Note: `inputs/FINAL-MANIFEST.sha256` is a record from the prior investigation
and references files (e.g. `COMPOSER-INPUT.md`, `CASE-STUDY.md`) that are not
present in this project; that is expected — it describes the frozen capsule of
the earlier run, not this directory.

## Read files (complete)

- START-HERE.md
- ASSIGNMENT.md
- INPUT-MANIFEST.sha256
- inputs/FINAL-RECONCILIATION.md
- inputs/MAIN-GLM-SYNTHESIS.md
- inputs/RUN-CARD.md
- inputs/STATUS.json
- inputs/VERIFICATION-RECEIPT.md
- inputs/FINAL-MANIFEST.sha256

## Local environment probe (read-only; nothing installed)

Python: 3.12.7

| Tool | Version | Role candidate |
|---|---|---|
| reportlab | 5.0.1 | PDF builder |
| pypdf | 6.14.2 | builder-side extractor / PDF surgery |
| Pillow | 11.3.0 | pixel accounting |
| pytest | present | test runner |
| pdftotext (poppler) | 26.09.0 | independent verifier extractor |
| pdftoppm (poppler) | 26.09.0 | independent renderer |
| pdfinfo (poppler) | 26.09.0 | independent page geometry |

Absent (recorded, not installed): mutool, qpdf, gs, pikepdf, pdfminer, PyMuPDF,
fpdf, weasyprint, pdfrw, exiftool.

## Ten-lane skeleton created

`lanes/01-…` through `lanes/10-…` created empty; `workspace/`, `outputs/`,
`receipts/` created. Wave A lanes 01–05 are independent; lane 06 runs only
after 01–05; Gate A is mechanical; Waves B and C run only if Gate A passes.

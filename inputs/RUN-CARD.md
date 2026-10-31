# Online PDF Reconstruction — Investigation Run Card

Date: 2026-09-29

## Objective

Test and refine a standalone document-reconstruction product whose first slice is:

> Input an ugly or poorly formatted PDF, produce a genuinely nicer reorganized PDF, and prove that meaning was preserved.

PDF Workbench is not a Phase 0 dependency. It may contribute isolated, license-compatible ideas later.

## Frozen source

- Capsule: `/Users/carrie/projects/chad-testing/pdfworkbench-investigation-2026-09-23/online-pdf-reconstruction-2026-09-29`
- Manifest: `SOURCE-MANIFEST.json`
- Verified: 19/19 files, byte sizes and SHA-256 values match; `data/` empty.

## Authorized sequence

1. One exact-model readiness canary for `glm-5.3-flashx`; no fallback.
2. Five substantive GLM FlashX investigation seats, with at most four concurrent calls on the Z.AI account:
   - forms and intake packets;
   - dense reports and long-form documents;
   - tables, statements, and data-heavy PDFs;
   - scans/OCR and mixed raster/vector PDFs;
   - hostile, ambiguous, inaccessible, and refusal cases.
3. Main reviews all five outputs, reconciles contradictions, and freezes one synthesis.
4. Composer receives that synthesis for three five-seat waves:
   - 5 MiMo;
   - 5 DeepSeek;
   - 5 SWE.

## Boundaries

- Research and implementation-readiness only; no install or live replacement.
- No paid fallback, silent model substitution, or global queue driver.
- Workers may read only the frozen capsule and write only their own output directory.
- Original PDFs remain immutable; generated documents are companions.
- Unknown, ambiguous, or unsafe reconstruction must be reported or refused, never guessed.

## Canary receipt

- Endpoint: Z.AI coding-plan OpenAI-compatible route
- Requested/reported model: `glm-5.3-flashx`
- Result: HTTP 200
- Usage: 65 prompt + 96 completion/reasoning = 161 tokens
- No fallback or retry reached the provider.


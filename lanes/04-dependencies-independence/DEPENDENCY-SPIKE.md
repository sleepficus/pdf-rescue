# DEPENDENCY-SPIKE.md — lane 04 repair (sealed-packet evidence only)

Spec `1.0.0-repair1` · 2026-09-29 · Basis: `ENVIRONMENT-INVENTORY.md` sealed observations. This seat ran no new inspection, installed nothing, changed nothing. Absent tools are recorded, never installed (fail closed).

### 1. Observed inventory and frozen roles

| Tool / version | Lineage | Frozen role(s) |
|---|---|---|
| reportlab 4.4.9 | BUILDER | Builder page-content writer only. |
| pypdf 6.10.0 | BUILDER | Builder object surgery (trailer /ID, metadata, outline/link annots) and frozen planning-time extractor. BANNED for every verifier-decisive computation. |
| pdftotext 26.09.0 (/opt/homebrew/bin) | POPPLER | Independent second extractor (G3, plain + -layout); layout-order derivation via -bbox-layout (G5); geometry cross-check (G2). |
| pdftoppm 26.05.0 (bundled override path; exact path not stated in sealed inventory) | POPPLER | Independent renderer at 150 DPI (G4, G10). |
| pdfinfo 26.05.0 (bundled override path; exact path not stated in sealed inventory) | POPPLER | Page count/box cross-check (G1, G2); R01 encrypted-control observation. |
| pdfplumber 0.11.9 (engine: pdfminer.six) | PDFMINER_SIX | G4 text layer; G7 table detector + cell extraction; G2 primary geometry; G6 link annots via public API; G8 parsed-object scan. |
| pdfminer.six direct import | PDFMINER_SIX | G1 raw object inventory; G5 structure-tree derivation; G6 outline/dest traversal. CONDITIONAL on C1/C2. |
| shasum -a 256 / sha256sum; /usr/bin/time -l; du | OS_UTIL | G1 hashing; G9 CPU/wall/temp budgets. |
| Pillow 12.3.0 | HARNESS | PNG pixel accounting for G9 only; never parses PDFs. |
| CPython 3.12.14 stdlib socket audit hook | HARNESS | G9 no-network evidence. |
| verifier-owned stdlib raw-object scanner | VERIFIER_STDLIB_PENDING | Fallback: G1 inventory, G6 outline traversal. UNPROVEN until built by lane 09 and accepted at Gate A (C3). |

Absent, recorded not installed: qpdf, mutool, Ghostscript (gs), pikepdf, standalone pdfminer (importability contested, see C1), PyMuPDF.

### 2. Mechanical builder/verifier independence argument

- Definition (L01 §4): a decisive computation is independent iff (a) the verifier tool is not the builder's writer library and shares no decisive code path for that computation, (b) it is never invoked through builder APIs, and (c) the role is recorded in TOOLCHAIN.json.
- Builder decisive code paths = reportlab writer + pypdf object model. Verifier decisive paths = Poppler, pdfminer.six, OS utilities, harness, pending verifier stdlib. The sets are disjoint, so builder-vs-verifier independence holds for every gate whose decisive tool is drawn only from verifier lineages.
- POPPLER tools share one parsing core: pdftotext / pdftoppm / pdfinfo must never form an independence pair with each other. Therefore the G10 ink-vs-text comparison extractor is frozen to pdfplumber (PDFMINER_SIX), never pdftotext, so renderer and decisive extractor differ in lineage.
- The builder planning-time extractor is frozen to pypdf, so pdftotext satisfies G3's requirement of a lineage different from both builder writer and planner.
- Version skew pdftotext 26.09.0 vs pdftoppm/pdfinfo 26.05.0 is recorded; it does not weaken the lineage rule (same lineage, never paired) and receipts must cite the exact versions used.

### 3. Gate → tool verdicts (fail closed)

| Gate | Decisive verifier tools | Verdict |
|---|---|---|
| G1 | shasum + pdfminer.six inventory (C1) or scanner (C3) + pdfinfo | CONDITIONAL |
| G2 | pdfplumber + pdftotext -bbox-layout | MET |
| G3 | pdftotext | MET |
| G4 | pdftoppm + pdfplumber | MET |
| G5 | pdftotext -bbox-layout + pdfminer.six structure tree (C2) | CONDITIONAL |
| G6 | pdfplumber.hyperlinks + pdfminer.six traversal (C1/C2) or scanner (C3); pypdf banned | CONDITIONAL |
| G7 | pdfplumber table detector + verifier numeric lexer over pdfminer.six text | MET |
| G8 | stdlib/grep raw byte scan + pdfplumber parsed-object scan | MET |
| G9 | /usr/bin/time -l, du, Pillow PNG accounting, socket audit hook | MET iff harness observation present; also requires lane 05 BUDGETS.json (not in this packet) |
| G10 | pdftoppm renders + pdfplumber text layer (frozen pairing) | MET under the frozen pairing; if rejected, NOT_EXERCISED (no second renderer lineage exists) |

Fail-closed rule: unproven independence or absent tool ⇒ that gate records NOT_EXERCISED (never PASS); REQUIRED gates then yield NOT_VERIFIABLE via PR-08. No rule is weakened to rescue a verdict.

### 4. Capability checks (frozen, read-only, Gate A prerequisites)

- C1 — resolve the sealed-evidence conflict: the inventory lists pdfplumber 0.11.9 installed (its engine is pdfminer.six) while L03-ORACLE-NOTES §5 says no pdfminer on this machine. Command: python3 -c "import pdfminer; print(pdfminer.__version__)". On fail: G1/G5/G6 dependent roles are NOT_EXERCISED.
- C2 — structure-tree derivation probe: read a tagged one-page candidate structure tree with pdfminer.six only (no pypdf/reportlab code path). On fail: the G5 second derivation is NOT_DERIVABLE ⇒ G5 NOT_EXERCISED for affected documents.
- C3 — verifier-owned scanner acceptance: stdlib-only import audit plus Gate A diff review. On fail: the scanner serves no decisive role.

### 5. Validation checklist (executable)

- [ ] python3 -c "import reportlab, pypdf, pdfplumber, PIL" succeeds and versions match this file; mismatch ⇒ STOP with NOT_READY.
- [ ] pdftotext -v; pdftoppm -v; pdfinfo -v — record versions; mismatch with TOOLCHAIN.json ⇒ dependent gate roles NOT_EXERCISED.
- [ ] command -v qpdf mutool gs returns nothing; if found, they remain unselected.
- [ ] Run C1, C2, C3; record results verbatim in the run receipt.
- [ ] Assert no gate's decisive tool is reportlab or pypdf and no gate pairs two POPPLER tools.
- [ ] Any failed check ⇒ dependent gates recorded NOT_EXERCISED honestly; no substitution invented.


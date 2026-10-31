# LICENSE-NOTES.md — lane 04 repair

Method: the sealed packet contains no license files or license statements. Licenses below are upstream-declared licenses associated with the observed versions; none are verified by this seat. They are recorded UNKNOWN-UNVERIFIED and must remain UNKNOWN until supported by a citable artifact (per ENVIRONMENT-INVENTORY.md: unknown license facts stay unknown unless supported by supplied evidence).

| Component | Version | Upstream license (declared, unverified) | Status |
|---|---|---|---|
| Python (bundled) | 3.12.14 | PSF-2.0 | UNKNOWN-UNVERIFIED |
| reportlab | 4.4.9 | BSD-3-Clause | UNKNOWN-UNVERIFIED |
| pypdf | 6.10.0 | BSD-3-Clause | UNKNOWN-UNVERIFIED |
| pdfplumber | 0.11.9 | MIT | UNKNOWN-UNVERIFIED |
| pdfminer.six (pdfplumber engine) | UNKNOWN | MIT | UNKNOWN (version unproven, check C1) |
| Poppler pdftotext | 26.09.0 | GPL-2.0-or-later | UNKNOWN-UNVERIFIED |
| Poppler pdftoppm, pdfinfo | 26.05.0 | GPL-2.0-or-later | UNKNOWN-UNVERIFIED |
| Pillow | 12.3.0 | HPND / MIT-CMU | UNKNOWN-UNVERIFIED |

Frozen rules:

1. No installs, downloads, or package-manager writes: nothing new is brought onto the machine, so no new license obligation is knowingly created.
2. This is a private, local, non-redistributing experiment. The effect of invoking GPL-2.0-or-later Poppler binaries as separate processes on this run or its artifacts is UNKNOWN; legal assessment is out of scope for this lane and nothing is claimed either way.
3. License status never relaxes an independence or fail-closed rule; no tool is substituted or added for license reasons without recorded evidence.
4. Receipts must cite exact versions used, including the recorded skew pdftotext 26.09.0 vs pdftoppm/pdfinfo 26.05.0.

Validation checklist (executable):

- [ ] grep lane logs for pip, brew, npm install commands: none present.
- [ ] Receipt tool versions match TOOLCHAIN.json exactly.
- [ ] Every table row still reads UNKNOWN-UNVERIFIED unless a license artifact was added with a path citation.

